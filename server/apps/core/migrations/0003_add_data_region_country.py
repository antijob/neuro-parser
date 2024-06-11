from django.db import migrations, models
import django.db.models.deletion
from server.apps.core.data.regions import COUNTRIES, REGIONS
from server.apps.core.models import Country, Region

def add_country_regions(apps, schema_editor):
    """
    adds initial countries and regions data
    """
    for country in COUNTRIES:
        Country.objects.get_or_create(name=country[0])
    for region in REGIONS:
        Region.objects.get_or_create(
            name=region[0], country=Country.objects.get(name="RUS")
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_create_region_country"),
    ]

    operations = [
        migrations.RunPython(add_country_regions),
    ]
