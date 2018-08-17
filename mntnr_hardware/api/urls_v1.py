from rest_framework import routers
from django.conf.urls import include, url

from mntnr_hardware.api import views
from mntnr_hardware.api import viewsets


router = routers.SimpleRouter()
router.register(r'cabinets', viewsets.CabinetModelViewSet)
router.register(r'cabinet-assignments', viewsets.CabinetAssignmentModelViewSet)
router.register(r'datacenters', viewsets.DatacenterModelViewSet)
router.register(r'network-devices', viewsets.NetDeviceModelViewSet)
router.register(r'pdus', viewsets.PduModelViewSet)
router.register(r'port-assignments', viewsets.PortAssignmentModelViewSet)
router.register(r'servers', viewsets.ServerModelViewSet)


urlpatterns = [
    url(r'^$', views.api_root, name='hardware-root'),
    url(r'^', include(router.urls, namespace='hardware')),
]
