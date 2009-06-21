from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'openkansas_api.views',
    url(r'^(representative|senator)/(\d+)/(.+)?$', 'handle_details', name="openkansas_api_details"),
    url(r'^$', 'handle_query', name="openkansas_api_query"),
)

