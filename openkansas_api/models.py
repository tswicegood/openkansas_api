from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ImproperlyConfigured
from geopy import geocoders
import re

if not hasattr(settings, 'GOOGLE_MAPS_KEY'):
    raise ImproperlyConfigured(
        "openkansas_api requires a GOOGLE_MAPS_KEY configuration "
        "setting.  Please add it to your settings.py file."
    )

geocoder = geocoders.Google(settings.GOOGLE_MAPS_KEY)

TYPE_CHOICES = (
    ('REP', 'Representative'),
    ('SEN', 'Senator'),
)

PARTY_CHOICES = (
    ('D', 'Democrat'),
    ('R', 'Republican'),
)

class RepresentativeManager(models.GeoManager):
    def by_geocode(self, query):
        place, (lat, lng) = geocoder.geocode(query)
        return (
            {
                'place': place,
                'lat': lat,
                'lng': lng,
            },
            self.with_lat_lng(lat, lng)
        )

    def with_lat_lng(self, lat, lng):
        return self.filter(poly__contains='POINT(%s %s)' % (lng, lat))

    def with_district_first_and_last_names(self, district, first_name, last_name):
        return self.filter(district = district, first_name__contains = first_name,
                           last_name__contains = last_name)

    def with_district_and_last_name(self, district, last_name):
        return self.filter(district = district, last_name__contains = last_name)

class Representative(models.Model):
    district = models.IntegerField()
    type = models.CharField(max_length = 3, choices=TYPE_CHOICES)
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    party = models.CharField(max_length = 3, choices=PARTY_CHOICES)
    poly=models.PolygonField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    objects = RepresentativeManager()
    nick_name_matcher = re.compile(".*\(([^)]+)\).*")

    def get_url_name(self):
        return self.full_name.replace(' ', '-')
    url_name = property(get_url_name)

    def fetch_image_url(self):
        match = self.__class__.nick_name_matcher.match(self.first_name)
        if match is not None:
            first_name = match.groups()[0]
        else:
            first_name = self.first_name.split(' ')[0]

        return "http://www.kslegislature.org/%sroster/images/%s,%s.jpg" % (
            {'SEN': 'senate', 'REP': 'house'}[self.type],
            self.last_name.lower(), first_name.lower()
        )

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
    full_name = property(get_full_name)

    def get_party_adjective(self):
        return {
            'R': 'Republican',
            'D': 'Democratic',
        }[self.party]

    def get_official_phone(self):
        try:
            return self.phone_numbers.filter(type = 'O')[0]
        except IndexError:
            pass
    official_phone = property(get_official_phone)

    def __unicode__(self):
        return "District #%s: %s, %s (%s)" % (
            self.district,
            self.last_name,
            self.first_name,
            self.party,
        )

class AddressManager(models.GeoManager):
    def create_from_geo(self, query, rep):
        try:
            # Always guess that Google knows best
            place, (lat, lng) = [r for r in geocoder.geocode(query + ", KS", exactly_one = False)][0]
            exploded = place.split(',')
            if len(exploded) == 4:
                street_address = exploded[0].strip()
                city = exploded[1].strip()
                zipcode = exploded[2].strip()[3:]
            else:
                city = exploded[1].strip()
                street_address = query.rstrip(city)
                zipcode = None
        
        except IndexError:
            """
            We generate an IndexError in the list comprehension above if nothing
            is found.  Catch it here and try to parse it as some sort of special
            postal box.

            @TODO: Also try matching against Road, Rd, Street, St, Avenue, Ave,
                   etc., etc. to try and find a match.
            """
            matches = re.compile('^(.*Box \d+) ([A-Za-z ]+)$').match(query)
            if matches is None:
                return None
            values = matches.groups()
            street_address = values[0]
            city = values[1]
            zipcode = None
            place, (lat, lng) = geocoder.geocode(city + ', KS')

        address = self.create(
            street_address = street_address,
            city = city,
            zipcode = zipcode,
            representative = rep,
            point = 'POINT(%s %s)' % (lng, lat),
        )
        return address


class Address(models.Model):
    street_address = models.CharField(max_length = 255)
    street_address_2 = models.CharField(max_length = 255, blank = True, null = True)
    city = models.CharField(max_length = 255)
    zipcode = models.CharField(max_length = 10, blank = True, null = True)
    type = models.CharField(max_length = 10)
    point = models.PointField()
    representative = models.ForeignKey(Representative, related_name="addresses")

    objects = AddressManager()

    def __unicode__(self):
        return "%s: %s, %s" % (self.type, self.street_address, self.city)

class EmailAddress(models.Model):
    email = models.EmailField()
    type = models.CharField(max_length = 25)
    representative = models.ForeignKey(Representative, related_name="email_addresses")

class CapitalOffice(models.Model):
    room = models.CharField(max_length = 25)
    representative = models.ForeignKey(Representative, related_name="offices")


PHONE_TYPE_CHOICES = (
    ('O', 'Office'),
    ('H', 'Home'),
)

class Phone(models.Model):
    phone = models.CharField(max_length = 20)
    type = models.CharField(max_length = 1, choices=PHONE_TYPE_CHOICES)
    representative = models.ForeignKey(Representative, related_name="phone_numbers")

    def __unicode__(self):
        return self.phone

