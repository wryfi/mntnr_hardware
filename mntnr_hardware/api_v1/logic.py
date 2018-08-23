from uuid import UUID

from mountaineer.app import db
from mntnr_hardware.models import Datacenter
from .serializers import  datacenter_serializer


def say_hello():
    return {'hello': 'world'}


def datacenter_create(datacenter):
    deserialized = datacenter_serializer.deserialize(datacenter)
    datacenter = Datacenter(**deserialized)
    db.session.add(datacenter)
    db.session.commit()
    return datacenter_serializer.serialize(datacenter), 201


def datacenter_delete(id):
    datacenter = db.session.query(Datacenter).filter(Datacenter.id == id).first()
    db.session.delete(datacenter)
    db.session.commit()
    return {'deleted': 'datacenter {}'.format(id)}, 200


def datacenter_detail(id):
    datacenter = db.session.query(Datacenter).filter(Datacenter.id == id).first()
    return datacenter_serializer.serialize(datacenter)


def datacenter_update(id, datacenter):
    deserialized = datacenter_serializer.deserialize(datacenter)
    datacenter = db.session.query(Datacenter).filter(Datacenter.id == id).first()
    for key, value in deserialized.items():
        if value:
            setattr(datacenter, key, value)
    db.session.commit()
    return datacenter_serializer.serialize(datacenter), 200


def datacenters_list():
    datacenters = db.session.query(Datacenter).all()
    return [datacenter_serializer.serialize(datacenter) for datacenter in datacenters]
