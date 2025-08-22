from typing import Optional

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify

from ninja import Field, Router, ModelSchema, FilterSchema, Query

from api_auth import api_key

from bands.models import Venue, Room, Musician, Band

router = Router()


class RoomSchema(ModelSchema):
    class Meta:
        model = Room
        fields = ["id", "name"]


class MusicianSchema(ModelSchema):
    class Meta:
        model = Musician
        fields = ["first_name", "last_name", "birth", "description"]


class BandOut(ModelSchema):
    slug: str
    url: str

    musicians: list[MusicianSchema] = Field(..., alias="musicians")

    class Meta:
        model = Band
        fields = ["name"]

    @staticmethod
    def resolve_slug(obj):
        slug = slugify(obj.name) + "-" + str(obj.id)
        return slug

    @staticmethod
    def resolve_url(obj):
        url = reverse("api-1.0:fetch_band", args=[obj.id])
        return url


class VenueOut(ModelSchema):
    slug: str
    url: str

    rooms: list[RoomSchema] = Field(..., alias="room_set")

    class Meta:
        model = Venue
        fields = ["id", "name", "description"]

    @staticmethod
    def resolve_slug(obj):
        slug = slugify(obj.name) + "-" + str(obj.id)
        return slug

    @staticmethod
    def resolve_url(obj):
        url = reverse("api-1.0:fetch_venue", args=[obj.id])
        return url


class VenueIn(ModelSchema):
    class Meta:
        model = Venue
        fields = ["name", "description"]


class VenueFilter(FilterSchema):
    name: Optional[str] = Field(None, q=["name__istartswith"])


class MusicianIn(ModelSchema):
    class Meta:
        model = Musician
        fields = ["first_name", "last_name", "birth", "description"]


class BandFilter(FilterSchema):
    name: Optional[str] = Field(None, q=["name__istartswith"])


@router.get("/venue/{venue_id}/", response=VenueOut, url_name="fetch_venue")
def fetch_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return venue


@router.get("/venues/", response=list[VenueOut])
def venues(request, filters: VenueFilter = Query(...)):
    venues = Venue.objects.all()
    venues = filters.filter(venues)
    return venues


@router.post("/venue/", response=VenueOut, auth=api_key)
def create_venue(request, payload: VenueIn):
    venue = Venue.objects.create(**payload.dict())
    return venue


@router.put("/venue/{venue_id}", response=VenueOut, auth=api_key)
def update_venue(request, venue_id, payload: VenueIn):
    venue = get_object_or_404(Venue, id=venue_id)
    for key, val in payload.dict().items():
        setattr(venue, key, val)
    venue.save()
    return venue


@router.put("/musician/{musician_id}/", response=MusicianSchema, auth=api_key)
def update_musician(request, musician_id, payload: MusicianIn):
    musician = get_object_or_404(Musician, id=musician_id)
    for key, val in payload.dict().items():
        setattr(musician, key, val)
    musician.save()
    return musician


@router.delete("/venue/{venue_id}/", auth=api_key)
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    venue.delete()

    return {"success": True}


@router.get("/band/{band_id}", response=BandOut, url_name="fetch_band")
def bands(request, band_id):
    bands = get_object_or_404(Band, id=band_id)
    return bands


@router.get("/bands/", response=list[BandOut])
def bands(request, filters: BandFilter = Query(...)):
    bands = Band.objects.all()
    bands = filters.filter(bands)
    return bands
