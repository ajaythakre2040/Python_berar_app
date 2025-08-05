# location/serializers.py

from rest_framework import serializers
from ems.models.location_master import Country, State, City


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class StateSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = State
        fields = ["id", "name", "state_code", "country"]


class CitySerializer(serializers.ModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        model = City
        fields = ["id", "name", "state"]
