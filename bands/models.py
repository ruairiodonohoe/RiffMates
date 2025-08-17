from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth = models.DateField()

    def __str__(self):
        return f"Musician(id={self.id}, last_name={self.last_name})"

    class Meta:
        ordering = ["last_name", "first_name"]


class Venue(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"Venue (id={self.id}, name={self.name})"

    class Meta:
        ordering = ["name"]


class Room(models.Model):
    name = models.CharField(max_length=20)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return f"Room (id={self.id}, name={self.name})"

    class Meta:
        unique_together = [["name", "venue"]]
        ordering = ["name"]


class Band(models.Model):
    name = models.CharField(max_length=20)
    musicians = models.ManyToManyField(Musician)

    def __str__(self):
        return f"Band (id={self.id}, name={self.name})"

    class Meta:
        ordering = ["name"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    musician_profiles = models.ManyToManyField(Musician, blank=True)
    venues_controlled = models.ManyToManyField(Venue, blank=True)
