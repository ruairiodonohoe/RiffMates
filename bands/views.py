from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect


from bands.models import Musician, Band, Venue, UserProfile, Room
from bands.forms import VenueForm, MusicianForm


# Create your views here.


def musicians(request):
    all_musicians = Musician.objects.all().order_by("last_name")

    try:
        per_page = int(request.GET.get("per_page", 3))
    except ValueError:
        per_page = 3

    if per_page < 1:
        per_page = 1
    elif per_page > 100:
        per_page = 100

    paginator = Paginator(all_musicians, per_page)

    page_num = request.GET.get("page", 1)
    page_num = int(page_num)

    if page_num < 1:
        page_num = 1
    elif page_num > paginator.num_pages:
        page_num = paginator.num_pages

    page = paginator.page(page_num)

    data = {"musicians": page.object_list, "page": page, "per_page": per_page}

    return render(request, "musicians.html", data)


def bands(request):
    all_bands = Band.objects.all()

    try:
        per_page = int(request.GET.get("per_page", 3))
    except ValueError:
        per_page = 3

    if per_page < 1:
        per_page = 1
    elif per_page > 100:
        per_page = 100

    paginator = Paginator(all_bands, per_page)
    page_num = request.GET.get("page", 1)
    if page_num < 1:
        page_num = 1
    elif page_num > paginator.num_pages:
        page_num = paginator.num_pages

    page = paginator.page(page_num)

    data = {"bands": page.object_list, "page": page, "per_page": per_page}

    return render(request, "bands.html", data)


def band(request, band_id):
    band = get_object_or_404(Band, id=band_id)

    data = {"band": band}

    return render(request, "band.html", data)


def venues(request):
    all_venues = Venue.objects.all().order_by("name")
    profile = getattr(request.user, "userprofile", None)
    if profile:
        for venue in all_venues:
            profile = request.user.userprofile
            venue.controlled = profile.venues_controlled.filter(id=venue.id).exists()
    else:
        # Anonymous user
        for venue in all_venues:
            venue.controlled = False

    data = {"venues": all_venues}

    return render(request, "venues.html", data)


def has_venue(user):
    try:
        return user.userprofile.venues.exist()
    except UserProfile.DoesNotExist:
        return False


@user_passes_test(has_venue)
def venues_restricted(request):
    return venues(request)


@login_required
def restricted_page(request):
    data = {"title": "Restricted Page", "content": "<h1>You are logged in </h1>"}
    return render(request, "general.html", data)


@login_required
def musician_restricted(request, musician_id):
    musician = get_object_or_404(Musician, id=musician_id)
    profile = request.user.userprofile
    allowed = False

    if profile.musician_profiles.filter(id=musician_id).exists():
        allowed = True
    else:
        musician_profiles = set(profile.musician_profiles.all())
        for band in musician.band_set.all():
            band_musicians = set(band.musicians.all())
            if musician_profiles.intersection(band_musicians):
                allowed = True
                break

    if not allowed:
        raise Http404("Permission denied")

    content = f"""
        <h1>Musician Page: {musician.last_name}</h1>
    """

    data = {"title": "Musician Restricted", "content": content}

    return render(request, "general.html", data)


@receiver(post_save, sender=User)
def user_post_save(sender, **kwargs):
    # Create UserProfile object if User object is new
    # and not loaded from fixture
    if kwargs["created"] and not kwargs["raw"]:
        user = kwargs["instance"]
        try:
            # Double check UserProfile doesn't exist already
            # (admin might create it before the signal fires)
            UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            # No UserProfile exists for this user, create one
            UserProfile.objects.create(user=user)


@receiver(user_login_failed)
def login_failed_callback(sender, credentials, request, **kwargs):
    username = credentials.get("username", "<unknown>")
    path = request.path if request else "<no request>"
    print(f"Login failed for username '{username}' at path '{path}'")


@login_required
def edit_venue(request, venue_id=0):
    venue = None
    # If venue_id != 0, then we are editing an existing venue
    if venue_id != 0:
        # fetch object
        venue = get_object_or_404(Venue, id=venue_id)
        # Check user controls venue
        if not request.user.userprofile.venues_controlled.filter(id=venue_id).exists():
            raise Http404("Can only edit controlled venues")

    if request.method == "POST":
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            venue = form.save()
            if venue_id == 0:
                request.user.userprofile.venues_controlled.add(venue)
            return redirect("venues")
    else:
        form = VenueForm(instance=venue)

    data = {"form": form}
    return render(request, "edit_venue.html", data)


def musician(request, musician_id):
    musician = get_object_or_404(Musician, id=musician_id)
    user = request.user
    can_edit = False

    if user.is_authenticated:
        profile = getattr(user, "userprofile", None)
        if profile:
            if profile.musician_profiles.filter(id=musician_id).exists():
                can_edit = True
        if user.is_staff:
            can_edit = True

    data = {"musician": musician, "can_edit": can_edit}

    return render(request, "musician.html", data)


@login_required
def edit_musician(request, musician_id=0):
    musician = None
    user = request.user

    # If musician_id != 0, then editting already existing musician
    if musician_id != 0:
        # Get object
        musician = get_object_or_404(Musician, id=musician_id)
        profile = getattr(user, "userprofile", None)

        # Raise error if user is not staff, or if not owner of musician profile.
        if not (
            user.is_staff
            or (profile and profile.musician_profiles.filter(id=musician_id).exists())
        ):
            raise Http404("You do not have permission to edit this musician.")

    # Handle form POST
    if request.method == "POST":
        form = MusicianForm(request.POST, request.FILES, instance=musician)
        if form.is_valid():
            musician = form.save()
            # if new musician, add to user profile
            if musician_id == 0 and hasattr(user, "userprofile"):
                user.userprofile.musician_profiles.add(musician)
            return redirect("musician", musician_id=musician.id)
    else:
        form = MusicianForm(instance=musician)

    data = {"form": form}
    return render(request, "edit_musician.html", data)
