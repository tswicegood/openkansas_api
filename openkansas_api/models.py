from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ImproperlyConfigured
from geopy import geocoders

if not hasattr(settings, 'YAHOO_MAPS_APP_ID'):
    raise ImproperlyConfigured(
        "openkansas_api requires a YAHOO_MAPS_APP_ID configuration "
        "setting.  Please add it to your settings.py file."
    )

geocoder = geocoders.Yahoo(settings.YAHOO_MAPS_APP_ID)

TYPE_CHOICES = (
    ('REP', 'Representative'),
    ('SEN', 'Senator'),
)

class DistrictManager(models.GeoManager):
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
        return self.filter(district = district, first_name = first_name,
                           last_name = last_name)

class District(models.Model):
    district = models.IntegerField()
    type = models.CharField(max_length = 3, choices=TYPE_CHOICES)
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    party = models.CharField(max_length = 3)
    poly=models.PolygonField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    objects = DistrictManager()

    def __unicode__(self):
        return "District #%s: %s, %s (%s)" % (
            self.district,
            self.last_name,
            self.first_name,
            self.party,
        )

