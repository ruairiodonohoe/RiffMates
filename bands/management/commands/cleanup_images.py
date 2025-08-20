# bands/management/commands/cleanup_orphan_pictures.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bands.models import Musician, Venue


class Command(BaseCommand):
    """
    Scans MEDIA_ROOT for picture files that are no longer referenced by
    Musician.picture or Venue.picture and (optionally) deletes them.

    Defaults to DRY-RUN: prints what would be removed.
    Use --delete to actually remove files.
    """

    help = "Remove orphaned musician/venue picture files from MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Actually delete orphaned files (default is dry-run).",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Do not prompt for confirmation when using --delete.",
        )
        parser.add_argument(
            "--all-media",
            action="store_true",
            help="Scan all of MEDIA_ROOT (not just the upload_to subdirs).",
        )

    def handle(self, *args, **opts):
        media_root = getattr(settings, "MEDIA_ROOT", None)
        if not media_root:
            raise CommandError("MEDIA_ROOT is not configured.")
        media_root = Path(media_root).resolve()
        if not media_root.exists():
            raise CommandError(f"MEDIA_ROOT does not exist: {media_root}")

        delete = bool(opts.get("delete"))
        no_input = bool(opts.get("no_input"))
        scan_all = bool(opts.get("all_media"))

        # Gather upload_to subdirectories (if simple strings).
        upload_dirs = self._upload_dirs(media_root)
        if not scan_all and not upload_dirs:
            self.stdout.write(
                self.style.WARNING(
                    "Could not infer upload_to directories; falling back to scanning all of MEDIA_ROOT."
                )
            )
            scan_all = True

        # Build sets of referenced files and on-disk files.
        referenced = self._collect_referenced_paths(media_root)
        on_disk = self._collect_on_disk_paths(
            media_root, upload_dirs if not scan_all else None
        )

        # Orphans = on-disk files that no DB row references.
        orphans = on_disk.difference(referenced)
        missing = referenced.difference(
            on_disk
        )  # referenced in DB, but file missing on disk

        # Report
        self.stdout.write(self.style.MIGRATE_HEADING("Picture cleanup report"))
        self.stdout.write(f" MEDIA_ROOT: {media_root}")
        if upload_dirs and not scan_all:
            rels = ", ".join(str(p.relative_to(media_root)) for p in upload_dirs)
            self.stdout.write(f" Scanning:  {rels}")
        else:
            self.stdout.write(" Scanning:  (entire MEDIA_ROOT)")

        self.stdout.write(f" Referenced files: {len(referenced)}")
        self.stdout.write(f" Files on disk:    {len(on_disk)}")
        self.stdout.write(self.style.WARNING(f" Missing files:     {len(missing)}"))
        self._print_paths("Missing (DB references with no file):", missing, media_root)

        self.stdout.write(self.style.WARNING(f" Orphans to remove: {len(orphans)}"))
        self._print_paths("Orphans (exist on disk, not in DB):", orphans, media_root)

        if not orphans:
            self.stdout.write(self.style.SUCCESS("No orphaned files found."))
            return

        if not delete:
            self.stdout.write(
                self.style.NOTICE("\nDRY-RUN complete. No files were deleted.")
            )
            self.stdout.write(
                "Run again with --delete to remove the files shown above."
            )
            return

        if not no_input:
            confirm = (
                input(
                    f"\nAbout to DELETE {len(orphans)} file(s). This cannot be undone.\n"
                    "Type 'yes' to continue: "
                )
                .strip()
                .lower()
            )
            if confirm != "yes":
                self.stdout.write(self.style.NOTICE("Aborted by user."))
                return

        deleted = 0
        for p in sorted(orphans):
            try:
                p.unlink(missing_ok=True)
                deleted += 1
                if self.verbosity >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted: {p.relative_to(media_root)}")
                    )
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Failed to delete {p}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"\nDeleted {deleted} orphaned file(s)."))

    # ---------- helpers ----------

    def _upload_dirs(self, media_root: Path) -> Set[Path]:
        """Infer upload_to directories for the picture fields, if they are simple strings."""
        dirs: Set[Path] = set()
        for model, field_name in [(Musician, "picture"), (Venue, "picture")]:
            field = model._meta.get_field(field_name)
            upload_to = getattr(field, "upload_to", None)
            # Only handle simple string upload_to; if callable, we can't infer a fixed dir.
            if isinstance(upload_to, str) and upload_to:
                # Normalize to a directory inside MEDIA_ROOT.
                root = (media_root / upload_to).resolve()
                # If upload_to is a file-like path, keep the parent directory.
                dirs.add(root if root.is_dir() else root.parent)
        # Limit to paths under MEDIA_ROOT for safety.
        return {d for d in dirs if media_root in d.parents or d == media_root}

    def _collect_referenced_paths(self, media_root: Path) -> Set[Path]:
        """Build a set of absolute Paths for every file referenced by DB rows."""
        referenced: Set[Path] = set()
        for model, field_name in [(Musician, "picture"), (Venue, "picture")]:
            for obj in model.objects.all().only(field_name):
                f = getattr(obj, field_name, None)
                # f may be a FieldFile; .name is the relative path (e.g., "musicians/pic.png")
                name = getattr(f, "name", None)
                if not name:
                    continue
                p = (media_root / name).resolve()
                # Only include files that live under MEDIA_ROOT.
                if media_root in p.parents or p == media_root:
                    referenced.add(p)
        return referenced

    def _collect_on_disk_paths(
        self, media_root: Path, roots: Iterable[Path] | None
    ) -> Set[Path]:
        """Collect all actual files on disk under given roots (or entire MEDIA_ROOT)."""
        files: Set[Path] = set()

        def add_from(root: Path):
            if not root.exists():
                return
            for p in root.rglob("*"):
                if p.is_file():
                    files.add(p.resolve())

        if roots:
            for r in roots:
                add_from(r)
        else:
            add_from(media_root)

        # Safety: keep only files under MEDIA_ROOT.
        return {p for p in files if media_root in p.parents or p == media_root}

    def _print_paths(
        self, title: str, paths: Set[Path], media_root: Path, limit: int = 50
    ):
        if not paths:
            return
        self.stdout.write(self.style.HTTP_INFO(f"\n{title}"))
        for i, p in enumerate(sorted(paths)):
            if i >= limit:
                self.stdout.write(f"... and {len(paths) - limit} more")
                break
            try:
                rel = p.relative_to(media_root)
            except Exception:
                rel = p
            self.stdout.write(f" - {rel}")
