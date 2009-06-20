from django.contrib.gis.db import models

TYPE_CHOICES = (
    ('REP', 'Representative'),
    ('SEN', 'Senator'),
)

class DistrictManager(models.GeoManager):
    def with_lat_lng(self, lat, lng):
        return self.filter(poly__contains='POINT(%s %s)' % (lng, lat))

class District(models.Model):
    district = models.IntegerField()
    type = models.CharField(max_length = 3, choices=TYPE_CHOICES)
    first_name = models.CharField(max_length = 255)
    last_name = models.CharField(max_length = 255)
    party = models.CharField(max_length = 3)
    poly=models.PolygonField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    objects = DistrictManager()

    def __unicode__(self):
        return "District #%s: %s, %s (%s)" % (
            self.district,
            self.last_name,
            self.first_name,
            self.party,
        )

