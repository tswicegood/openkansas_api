from django.shortcuts import render_to_response
from openkansas_api.models import District
# Create your views here.

def handle_query(request):
    (geodata, object_list) = District.objects.by_geocode(request.GET['q'])
    return render_to_response('openkansas_api/list.html', {
        'object_list': object_list,
    })

def handle_details(request, type, district, *args):
    real_type = type[0:3].upper()
    district = District.objects.get(type = real_type, district = district)
    return render_to_response('openkansas_api/details.html', {
        "district": district,
    })
