

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)


class State(models.Model):
    name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
