from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^pn/(?P<backend>[^/]+)', views.PNView.as_view(), name="pn_view"),
    url(r'^buy/(?P<backend>[^/]+)/(?P<contenttype>[^/]+)/(?P<object_id>[^/]+)/$', views.BuyView.as_view(), name="buy_view"),
)
