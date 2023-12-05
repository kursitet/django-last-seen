from django.conf.urls import include, patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.shortcuts import redirect

from last_seen.models import clear_interval

admin.autodiscover()


def clear(request):
    """Test view to force clear interval of user."""
    clear_interval(request.user)
    return redirect('/admin')


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^test_project/', include('test_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^clear/', clear),
)
