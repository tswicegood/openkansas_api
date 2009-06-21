from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.utils.layermapping import LayerMapError
from openkansas_api.models import District

def set_type_to(type, lm_entry):
    d = District.objects.with_district_first_and_last_names(
        lm_entry['DISTRICT'].as_int(),
        lm_entry['FIRST_NAME'].as_string(),
        lm_entry['LAST_NAME'].as_string(),
    )[0]
    d.type = type
    d.save()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        source_file, type = args[0], args[1]
        mapping = {
            "district": "DISTRICT",
            "last_name": "LAST_NAME",
            "first_name": "FIRST_NAME",
            "party": "PARTY",
            "poly": "POLYGON",
        }
        lm = LayerMapping(District, source_file, mapping)
        lm.save(verbose=True)

        # manually loop over the fields and set the representative
        ds = DataSource(source_file)
        [set_type_to(args[1], entry) for entry in ds[0]]

