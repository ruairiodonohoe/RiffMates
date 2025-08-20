from django.core.management.base import BaseCommand
from bands.models import Venue


class Command(BaseCommand):
    help = "List registered musicians"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rooms",
            "-r",
            action="store_true",
            help=("Display rooms of venue."),
        )

    def handle(self, *args, **options):
        show_rooms = options["rooms"]

        for venue in Venue.objects.all():
            self.stdout.write(f"{venue.name}")
            if show_rooms:
                rooms = getattr(venue, "room_set", None)
                if rooms:
                    for room in rooms.all():
                        self.stdout.write(f"   - {room.name}")
                else:
                    self.stdout("   (No rooms)")
