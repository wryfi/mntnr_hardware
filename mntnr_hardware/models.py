import enum
from functools import partial
from uuid import uuid4

from sqlalchemy import Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from mountaineer.database import db
from sqlalchemy.ext.declarative import declared_attr

RequiredColumn = partial(db.Column, nullable=False)


class Datacenter(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    name = db.Column(db.String(64))
    vendor = db.Column(db.String(64))
    address = db.Column(db.String(255))
    noc_phone = db.Column(db.String(15))
    noc_email = db.Column(db.String(255))
    noc_url = db.Column(db.String(255))

    __tablename__ = 'hardware_datacenters'

    def __repr__(self):
        return '<Datacenter: {} ({})>'.format(self.name, self.vendor)


class CabinetAttachmentEnum(enum.Enum):
    CAGE_NUT_95 = '95mm cage nut'
    DIRECT_ATTACH = 'direct attachment'
    OTHER = 'other'


class CabinetFastenerEnum(enum.Enum):
    UNF_10_32 = 'UNF 10-32'
    UNC_12_24 = 'UNC 12-24'
    M5 = 'M5'
    M6 = 'M6'
    OTHER = 'other'


class Cabinet(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    name = db.Column(db.String(64))
    datacenter_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_datacenters.id'))
    datacenter = db.relationship('Datacenter', backref=db.backref('cabinets'), lazy=True)
    rack_units = db.Column(db.Integer)
    depth = db.Column(db.Numeric(4, 2))
    width = db.Column(db.Numeric(4, 2))
    attachment = db.Column(Enum(CabinetAttachmentEnum))
    fasteners = db.Column(Enum(CabinetFastenerEnum))

    __tablename__ = 'hardware_cabinets'

    def __repr__(self):
        return '<Cabinet: {} ({})>'.format(self.name, self.datacenter.name)

    @property
    def devices(self):
        return [assigned.device for assigned in self.cabinet_assignments]

    @property
    def power(self):
        watts = 0
        pdus = [assigned.device for assigned in self.cabinet_assignments if type(assigned.device) == PowerDistributionUnit]
        for pdu in pdus:
            if pdu.watts:
                watts += pdu.watts
        return watts

    @property
    def power_allocated(self):
        draw = 0
        for assigned in self.cabinet_assignments:
            if assigned.device.draw:
                draw += assigned.device.draw
        return draw

    @property
    def power_available(self):
        delta = self.power - self.power_allocated
        if delta > 0:
            return delta
        return 0


class DeviceOrientationEnum(enum.Enum):
    FRONT = 'front'
    REAR = 'rear'


class DeviceDepthEnum(enum.Enum):
    HALF = 'half'
    FULL = 'full'


class CabinetAssignment(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    cabinet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_cabinets.id'))
    cabinet = db.relationship('Cabinet', backref=db.backref('cabinet_assignments'), lazy=True)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'))
    device = db.relationship('Device', backref=db.backref('cabinet_assignments'), lazy=True)
    position = db.Column(db.Integer)
    orientation = db.Column(Enum(DeviceOrientationEnum))
    depth = db.Column(Enum(DeviceDepthEnum))

    __tablename__ = 'hardware_cabinet_assignments'

    def __repr__(self):
        return '<CabinetAssignment {} in {}>'.format(self.device.id, self.cabinet.name)


class Device(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    type = db.Column(db.String(50))

    __tablename__ = 'hardware_devices'
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'device'}


class DeviceMixin(object):
    manufacturer = db.Column(db.String(128))
    model = db.Column(db.String(128))
    serial = db.Column(db.String(128))
    asset_id = db.Column(db.String(36))
    asset_tag = db.Column(db.String(36))
    rack_units = db.Column(db.Integer())
    draw = db.Column(db.Integer())

    @declared_attr
    def __table_args__(cls):
        return (db.UniqueConstraint('manufacturer', 'model', 'serial'), )

    @property
    def cabinet(self):
        try:
            return self.cabinet_assignments[0].cabinet
        except IndexError:
            return

    @property
    def location(self):
        try:
            assign = self.cabinet_assignments[0]
            return assign.cabinet, assign.position
        except IndexError:
            return

    @property
    def pdus(self):
        return [(assigned.device, assigned.device_port) for assigned in self.assigned_ports if type(assigned.device) == PowerDistributionUnit]

    @property
    def uplinks(self):
        return [(assigned.device, assigned.device_port) for assigned in self.assigned_ports if type(assigned.device) == NetworkDevice]


class Server(DeviceMixin, Device):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'), primary_key=True)
    memory = db.Column(db.Integer())
    cores = db.Column(db.Integer())

    __tablename__ = 'hardware_servers'
    __mapper_args__ = {'polymorphic_identity': 'server'}

    def __repr__(self):
        return '<Server ({} {})>'.format(self.manufacturer, self.model)


class PortDeviceMixin(object):
    ports = db.Column(db.Integer())

    @property
    def connected_devices(self):
        assigned = db.session.query(PortAssignment).filter(PortAssignment.device == self)
        return [(assignment.connected_device, assignment.device_port) for assignment in assigned]

    @property
    def ports_available(self):
        start_ports = [port for port in range(1, self.ports + 1)]
        return [port for port in start_ports if port not in self.ports_used]

    @property
    def ports_used(self):
        assigned = db.session.query(PortAssignment).filter(PortAssignment.device == self)
        return [assignment.device_port for assignment in assigned]


class PowerDistributionUnit(DeviceMixin, PortDeviceMixin, Device):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'), primary_key=True)
    volts = db.Column(db.Integer())
    amps = db.Column(db.Integer())

    __tablename__ = 'hardware_power_distribution_units'
    __mapper_args__ = {'polymorphic_identity': 'power_distribution_unit'}

    def __repr__(self):
        return '<PowerDistributionUnit ({} amps @ {} volts)>'.format(self.amps, self.volts)

    @property
    def watts(self):
        return self.amps * self.volts


class NetworkDeviceSpeedEnum(enum.Enum):
    TEN = '10 Mbps'
    ONE_HUNDRED = '100 Mbps'
    GIGABIT = '1 Gbps'
    TEN_GIGABIT = '10 Gbps'
    FORTY_GIGABIT = '40 Gbps'


class NetworkInterconnectEnum(enum.Enum):
    RJ45 = 'RJ-45'
    TWINAX = 'Twinaxial'
    OTHER = 'other'


class NetworkDevice(DeviceMixin, PortDeviceMixin, Device):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'), primary_key=True)
    speed = db.Column(Enum(NetworkDeviceSpeedEnum))
    interconnect = db.Column(Enum(NetworkInterconnectEnum))

    __tablename__ = 'hardware_network_devices'
    __mapper_args__ = {'polymorphic_identity': 'network_device'}

    def __repr__(self):
        return '<NetworkDevice ({} {})>'.format(self.manufacturer, self.model)


class PortAssignment(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'))
    device = db.relationship('Device', backref=db.backref('port_assignments'), lazy=True, foreign_keys=[device_id])
    device_port = db.Column(db.Integer())
    connected_device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hardware_devices.id'))
    connected_device = db.relationship('Device', backref=db.backref('assigned_ports'), lazy=True, foreign_keys=[connected_device_id])

    __tablename__ = 'hardware_port_assignments'
    __table_args__ = (UniqueConstraint('device_id', 'device_port'),)

    def __repr__(self):
        return '<PortAssignment ({} {} port {})>'.format(self.device.manufacturer, self.device.model, self.device_port)



