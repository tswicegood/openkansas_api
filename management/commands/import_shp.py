from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from openkansas_api.models import District

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        mapping = {
            "district": "DISTRICT",
            "last_name": "REP_LASTNM",
            "first_name": "REP_1STNM",
            "party": "PARTY",
            "poly": "POLYGON",
        }
        lm = LayerMapping(District, args[0], mapping)
        lm.save(verbose=True)
