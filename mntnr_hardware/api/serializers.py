import pdb

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from mountaineer.core.api import fields as mtnr_fields
from mountaineer.core.utils import slug
from mntnr_hardware import (
    RackDepth, RackOrientation, SwitchSpeed, SwitchInterconnect, CabinetAttachmentMethod, CabinetFastener
)
from mntnr_hardware.api import fields as hw_fields
from mntnr_hardware.models import (
    Cabinet, CabinetAssignment, Datacenter, Device, NetworkDevice, PortAssignment, PowerDistributionUnit, Server
)


class DeviceIdModelSerializerMixin(serializers.HyperlinkedModelSerializer):
    device_id = serializers.SerializerMethodField()

    def get_device_id(self, obj):
        try:
            return obj.device.id
        except (AttributeError):
            return


class PduSerializer(DeviceIdModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(
        view_name='api_v1:hardware:powerdistributionunit-detail', lookup_field='slug'
    )
    watts = serializers.SerializerMethodField()
    cabinet = serializers.HyperlinkedRelatedField(
        view_name='api_v1:hardware:cabinet-detail', lookup_field='slug', read_only=True
    )

    class Meta:
        model = PowerDistributionUnit
        exclude = ('device',)

    def get_watts(self, obj):
        return obj.watts


class PduSerializerEmbedded(PduSerializer):
    class Meta:
        model = PowerDistributionUnit
        fields = ['device_type', 'url', 'slug', 'manufacturer', 'model', 'serial']


class ServerSerializer(DeviceIdModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:hardware:server-detail', lookup_field='slug')
    cabinet = serializers.HyperlinkedRelatedField(
        view_name='api_v1:hardware:cabinet-detail', lookup_field='slug', read_only=True
    )

    class Meta:
        model = Server
        exclude = ('device',)


class ServerSerializerEmbedded(ServerSerializer):
    class Meta:
        model = Server
        fields = ['device_type', 'url', 'slug', 'manufacturer', 'model', 'serial']


class NetworkDeviceSerializer(DeviceIdModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:hardware:networkdevice-detail', lookup_field='slug')
    speed = mtnr_fields.SerializerEnumField(enum=SwitchSpeed)
    interconnect = mtnr_fields.SerializerEnumField(enum=SwitchInterconnect)
    cabinet = serializers.HyperlinkedRelatedField(
        view_name='api_v1:hardware:cabinet-detail', lookup_field='slug', read_only=True
    )

    class Meta:
        model = NetworkDevice
        exclude = ('device',)


class NetworkDeviceSerializerEmbedded(ServerSerializer):
    class Meta:
        model = NetworkDevice
        fields = ['device_type', 'url', 'slug', 'manufacturer', 'model', 'serial']


def get_embedded_serializer(model):
    return {
        PowerDistributionUnit: PduSerializerEmbedded,
        Server: ServerSerializerEmbedded,
        NetworkDevice: NetworkDeviceSerializerEmbedded
    }.get(model)


class DatacenterSerializer(serializers.HyperlinkedModelSerializer):
    """
    does this docstring show up somewhere in the swagger ui?

    """
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:hardware:datacenter-detail', lookup_field='slug')
    slug = serializers.CharField(read_only=True, default=slug.slugid_nice())

    class Meta:
        model = Datacenter
        fields = '__all__'


class DatacenterSerializerEmbedded(DatacenterSerializer):
    class Meta:
        model = Datacenter
        fields = ['url', 'name', 'slug', 'vendor']
        read_only_fields = ['vendor', 'name', 'url']


class CabinetSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:hardware:cabinet-detail', lookup_field='slug')
    slug = serializers.CharField(read_only=True, default=slug.slugid_nice())
    datacenter = DatacenterSerializerEmbedded()
    attachment = mtnr_fields.SerializerEnumField(enum=CabinetAttachmentMethod)
    fasteners = mtnr_fields.SerializerEnumField(enum=CabinetFastener)
    power = serializers.SerializerMethodField()
    power_allocated = serializers.SerializerMethodField()
    power_unallocated = serializers.SerializerMethodField()

    class Meta:
        model = Cabinet
        fields = '__all__'

    def create(self, valid_data):
        print(valid_data)
        datacenter_data = valid_data.pop('datacenter')
        print(datacenter_data)
        datacenter = Datacenter.objects.get(slug=datacenter_data['slug'])
        if not datacenter:
            return Cabinet.objects.create(datacenter=datacenter, **valid_data)
        else:
            raise ValidationError('datacenter with slug {} does not exist'.format(datacenter_data['slug']))

    def get_power(self, obj):
        return obj.power

    def get_power_allocated(self, obj):
        return obj.power_allocated

    def get_power_unallocated(self, obj):
        return obj.power_unallocated

    def update(self, valid_data):
        print('can we haz update maybe?')


class CabinetSerializerEmbedded(CabinetSerializer):
    slug = serializers.CharField(default=None)

    class Meta:
        model = Cabinet
        fields = ['name', 'url', 'slug', 'datacenter']

    def create(self, valid_data):
        print('HOW ABOUT THIS ONE?')


class DeviceSerializer(serializers.Serializer):
    device_id = serializers.UUIDField()
    instance = serializers.SerializerMethodField()

    class Meta:
        fields = ['device_id']

    def get_instance(self, obj):
        device = Device.objects.get(id=obj.device_id)
        model_serializer = get_embedded_serializer(type(device.instance))
        serializer = model_serializer(device.instance, context=self.context)
        return serializer.data


class CabinetAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='api_v1:hardware:cabinetassignment-detail', lookup_field='slug'
    )
    slug = serializers.CharField(read_only=True, default=slug.slugid_nice())
    cabinet = serializers.HyperlinkedRelatedField(
        queryset=Cabinet.objects.all(), view_name='api_v1:hardware:cabinet-detail', lookup_field='slug'
    )
    cabinet_name = serializers.SerializerMethodField()
    cabinet_slug = serializers.SerializerMethodField()
    device_type = serializers.SerializerMethodField()
    device_id = serializers.UUIDField()
    device_slug = serializers.SerializerMethodField()
    device = hw_fields.HyperlinkedDeviceField(lookup_field='slug', read_only=True)
    device_name = serializers.SerializerMethodField()
    depth = mtnr_fields.SerializerEnumField(enum=RackDepth)
    orientation = mtnr_fields.SerializerEnumField(enum=RackOrientation)

    class Meta:
        model = CabinetAssignment
        fields = '__all__'

    def get_cabinet_name(self, obj):
        return obj.cabinet.name

    def get_cabinet_slug(self, obj):
        return obj.cabinet.slug

    def get_device_name(self, obj):
        return obj.device.instance.__str__()

    def get_device_slug(self, obj):
        return obj.device.instance.slug

    def get_device_type(self, obj):
        return obj.device.type.__qualname__


class PortAssignmentSerializer(DeviceIdModelSerializerMixin):
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:hardware:portassignment-detail', lookup_field='slug')
    device = hw_fields.HyperlinkedDeviceField(lookup_field='slug', read_only=True)
    device_id = serializers.UUIDField()
    device_name = serializers.SerializerMethodField()
    device_port = serializers.IntegerField()
    connected_device = hw_fields.HyperlinkedDeviceField(lookup_field='slug', read_only=True)
    connected_device_id = serializers.UUIDField()
    connected_device_name = serializers.SerializerMethodField()

    class Meta:
        model = PortAssignment
        fields = '__all__'

    def get_device_name(self, obj):
        return obj.device.instance.__str__()

    def get_connected_device_name(self, obj):
        return obj.connected_device.instance.__str__()
