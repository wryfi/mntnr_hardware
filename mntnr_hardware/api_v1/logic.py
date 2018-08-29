from mountaineer.app import db
from mountaineer.utils import get_object_or_404, validate_uuid

from mntnr_hardware.models import Cabinet, Datacenter, CabinetAssignment, Device


def say_hello():
    return {'hello': 'world'}


def datacenter_create(datacenter):
    datacenter = Datacenter(**datacenter)
    db.session.add(datacenter)
    db.session.commit()
    return datacenter.serialize(), 201


@validate_uuid
def datacenter_delete(id):
    datacenter = get_object_or_404(Datacenter, Datacenter.id == id)
    db.session.delete(datacenter)
    db.session.commit()
    return {'deleted': 'datacenter {}'.format(id)}, 200


@validate_uuid
def datacenter_detail(id):
    datacenter = get_object_or_404(Datacenter, Datacenter.id == id)
    return datacenter.serialize(), 201


@validate_uuid
def datacenter_update(id, datacenter):
    dc = get_object_or_404(Datacenter, Datacenter.id == id)
    for key, value in datacenter.items():
        if value:
            setattr(dc, key, value)
    db.session.commit()
    return dc.serialize(), 201


def datacenters_list():
    datacenters = db.session.query(Datacenter).all()
    return [datacenter.serialize() for datacenter in datacenters]


def cabinet_create(cabinet):
    dc = cabinet.pop('datacenter')
    datacenter = get_object_or_404(Datacenter, Datacenter.id == dc['id'])
    cabinet = Cabinet(**cabinet)
    cabinet.datacenter = datacenter
    db.session.add(cabinet)
    db.session.commit()
    return cabinet.serialize(detail=True), 201


@validate_uuid
def cabinet_delete(id):
    cabinet = get_object_or_404(Cabinet, Cabinet.id == id)
    db.session.delete(cabinet)
    db.session.commit()
    return {'deleted': 'cabinet {}'.format(id)}, 200


@validate_uuid
def cabinet_detail(id):
    cabinet = get_object_or_404(Cabinet, Cabinet.id == id)
    return cabinet.serialize(detail=True), 200


def cabinets_list():
    cabinets = db.session.query(Cabinet).all()
    return [cabinet.serialize() for cabinet in cabinets], 200


@validate_uuid
def cabinet_update(id, cabinet):
    cab = get_object_or_404(Cabinet, Cabinet.id == id)
    dc = cabinet.pop('datacenter')
    if dc.get('id'):
        cabinet['datacenter'] = get_object_or_404(Datacenter, Datacenter.id == dc['id'])
    for key, value in cabinet.items():
        if value:
            setattr(cab, key, value)
    db.session.commit()
    return cab.serialize(), 200


def cabinet_assignment_create(assignment):
    cab_data, device_data = assignment.pop('cabinet'), assignment.pop('device')
    cabinet = get_object_or_404(Cabinet, Cabinet.id == cab_data['id'])
    device = get_object_or_404(Device, Device.id == device_data['id'])
    cabinet_assignment = CabinetAssignment(**assignment)
    cabinet_assignment.cabinet = cabinet
    cabinet_assignment.device = device
    db.session.commit()
    return cabinet_assignment.serialize(), 201


def cabinet_assignments_list():
    assignments = db.session.query(CabinetAssignment).all()
    return [assignment.serialize() for assignment in assignments]


@validate_uuid
def cabinet_assignment_delete(id):
    assignment = get_object_or_404(CabinetAssignment, CabinetAssignment.id == id)
    db.session.delete(assignment)
    db.session.commit()
    return {'deleted': 'cabinet-assignment {}'.format(id)}


@validate_uuid
def cabinet_assignment_detail(id):
    assignment = get_object_or_404(CabinetAssignment, CabinetAssignment.id == id)
    return assignment.serialize(), 200


@validate_uuid
def cabinet_assignment_update(id, assignment):
    assigned = get_object_or_404(CabinetAssignment, CabinetAssignment.id == id)
    if assignment.get('cabinet'):
        cabinet = assignment.pop('cabinet')
        assignment['cabinet'] = get_object_or_404(Cabinet, Cabinet.id == cabinet['id'])
    if assignment.get('device'):
        device = assignment.pop('device')
        assignment['device'] = get_object_or_404(Device, Device.id == device['id'])
    for key, value in assignment.items():
        if value is not None:
            setattr(assigned, key, value)
    db.session.commit()
    return assigned.serialize(), 200
