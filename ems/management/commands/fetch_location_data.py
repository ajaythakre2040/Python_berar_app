import requests
from django.core.management.base import BaseCommand
from api_endpoints import EXTERNAL_LOCATION_API_BASE_URL
from ems.models.location_master import Country, State, City


class Command(BaseCommand):
    help = (
        "Fetch and store Indian states and cities from external API without duplicates"
    )

    def handle(self, *args, **kwargs):
        base_url = EXTERNAL_LOCATION_API_BASE_URL
        state_url = f"{base_url}/countries/states"
        city_url = f"{base_url}/countries/state/cities"

        country_name = "India"
        country_name = country_name.strip().title()

        self.stdout.write(f"\n🌍 Processing country: {country_name}")
        country_obj, _ = Country.objects.get_or_create(name=country_name)

        self.stdout.write("📥 Fetching states...")
        state_res = requests.post(state_url, json={"country": country_name})
        states = state_res.json().get("data", {}).get("states", [])

        for s in states:
            state_name = s["name"].strip().title()
            state_code = s.get("state_code", "").strip().upper()

            self.stdout.write(f"  🏛️  State: {state_name} ({state_code})")

            state_obj, created = State.objects.get_or_create(
                name=state_name,
                country=country_obj,
                defaults={"state_code": state_code},
            )

            if not created and state_code and state_obj.state_code != state_code:
                state_obj.state_code = state_code
                state_obj.save()

            # Fetch Cities
            city_res = requests.post(
                city_url, json={"country": country_name, "state": state_name}
            )
            cities = city_res.json().get("data", [])

            for c in cities:
                city_name = c.strip().title()
                _, created = City.objects.get_or_create(name=city_name, state=state_obj)
                if created:
                    self.stdout.write(f"    ➕ City added: {city_name}")
                else:
                    self.stdout.write(f"    🔁 City exists: {city_name}")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Import complete: States and Cities saved.")
        )
