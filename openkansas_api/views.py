from django.shortcuts import render_to_response, redirect
from openkansas_api.models import Representative
# Create your views here.

def handle_query(request, query = None):
    if query is None:
        if request.GET.has_key('q'):
            return redirect('openkansas_api_query', request.GET['q'])
        else:
            return redirect('openkansas_api_index')

    (geodata, object_list) = Representative.objects.by_geocode(query)
    return render_to_response('openkansas_api/list.html', {
        'object_list': object_list,
    })

def handle_index(request):
    return render_to_response('openkansas_api/search.html')

def handle_details(request, type, district, *args):
    real_type = type[0:3].upper()
    representative = Representative.objects.get(type = real_type, district = district)
    return render_to_response('openkansas_api/details.html', {
        "representative": representative,
    })
