from piston.handler import BaseHandler
from openkansas_api.models import Representative

REPRESENTATIVE_FIELDS = (
    'district',
    'type',
    'full_name',
    ('home_address', (
        'street_address',
        'city',
        'state',
        'zipcode',
        'lat',
        'lng',
    )),
    ('offices', (
        'room',
    )),
    ('phone_numbers', (
        'type',
        'phone',
    )),
)


class RepresentativeHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Representative
    fields = REPRESENTATIVE_FIELDS
    
    def read(self, request, type, district):
        real_type = type[0:3].upper()
        representative = Representative.objects.get(type = real_type, district = district)
        return representative


class RepresentativeWithPolyHandler(RepresentativeHandler):
    fields = REPRESENTATIVE_FIELDS + ('poly',)


class SearchHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Representative
    fields = REPRESENTATIVE_FIELDS

    def read(self, request, query):
        _, ret = Representative.objects.by_geocode(query)
        return ret
