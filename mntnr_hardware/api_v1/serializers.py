"""
Connexion does type validation for all the OpenAPI v2 data types, so we don't
need to do it here. See https://goo.gl/tuEhoz for a list of these data types
and how they map to the OpenAPI schema.

The fields defined on the serializers below simply as 'field' rely on connexion
for type validation via the OpenAPI schema.  Validating again at the serializer
level would only incur unnecessary overhead.

"""

from strainer import (child, field, serializer)

from mountaineer.strain import enum_validator, email_field, enum_field, url_field, uuid_field

from mntnr_hardware.models import CabinetAttachmentEnum, CabinetFastenerEnum


datacenter_serializer = serializer(
    uuid_field('id'),
    field('name'),
    field('vendor'),
    field('address'),
    field('noc_phone'),
    email_field('noc_email'),
    url_field('noc_url')
)


datacenter_embedded_serializer = serializer(
    uuid_field('id'),
    field('name')
)


cabinet_serializer = serializer(
    uuid_field('id'),
    field('name'),
    child('datacenter', serializer=datacenter_embedded_serializer),
    field('rack_units'),
    field('depth'),
    field('width'),
    enum_field('attachment', validators=[enum_validator(enum=CabinetAttachmentEnum)]),
    enum_field('fasteners', validators=[enum_validator(enum=CabinetFastenerEnum)])
)

