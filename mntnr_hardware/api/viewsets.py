from rest_framework.viewsets import ModelViewSet

from mntnr_hardware.api.serializers import (
    CabinetSerializer, CabinetAssignmentSerializer, DatacenterSerializer, NetworkDeviceSerializer,
    PduSerializer, PortAssignmentSerializer, ServerSerializer
)
from mntnr_hardware.models import (
    Cabinet, CabinetAssignment, Datacenter, NetworkDevice, PortAssignment, PowerDistributionUnit, Server
)


class SlugModelViewSet(ModelViewSet):
    lookup_field = 'slug'


class DatacenterModelViewSet(SlugModelViewSet):
    queryset = Datacenter.objects.all()
    serializer_class = DatacenterSerializer


class CabinetModelViewSet(SlugModelViewSet):
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer


class CabinetAssignmentModelViewSet(SlugModelViewSet):
    queryset = CabinetAssignment.objects.all()
    serializer_class = CabinetAssignmentSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class ServerModelViewSet(SlugModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


class PduModelViewSet(SlugModelViewSet):
    queryset = PowerDistributionUnit.objects.all()
    serializer_class = PduSerializer


class NetDeviceModelViewSet(SlugModelViewSet):
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceSerializer


class PortAssignmentModelViewSet(SlugModelViewSet):
    queryset = PortAssignment.objects.all()
    serializer_class = PortAssignmentSerializer