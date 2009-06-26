from django.core.management.base import BaseCommand
from openkansas_api.models import Representative, Link
import yaml

def add_link(data):
    link = Link.objects.create_link_for_rep(
        title = data['title'],
        url = data['url'],
        representative = data['name']
    )
    link.save()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        f = open(args[0])
        y = yaml.load(f)
        [add_link(data) for data in y["links"]]
