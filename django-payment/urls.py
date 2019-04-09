from django.conf.urls import patterns
from django.conf.urls import url

from payment import views

urlpatterns = patterns(
    '',
    url(r'^pn/(?P<backend>[^/]+)',
        views.PNView.as_view(),
        name="pn_view"),
)
