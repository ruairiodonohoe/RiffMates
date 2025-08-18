from django import forms
from bands.models import Venue

VenueForm = forms.modelform_factory(Venue, fields=["name", "description", "picture"])
