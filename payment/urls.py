from django.urls import re_path as url

from . import views

urlpatterns = (
    url(r'^pn/(?P<backend>[^/]+)', views.PNView.as_view(), name="pn"),
    url(r'^buy/$', views.BuyView.as_view(), name="buy"),
)
