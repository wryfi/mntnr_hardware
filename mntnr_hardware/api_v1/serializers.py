from strainer import (child, field, formatters, serializer, ValidationException, validators)

from mountaineer.formatters import enum_formatter


# TODO: create a uuid formatter and/or validator
datacenter_serializer = serializer(
    field('id'),
    field('name'),
    field('vendor'),
    field('address'),
    field('noc_phone'),
    field('noc_email'),
    field('noc_url')
)


datacenter_embedded_serializer = serializer(
    field('id'),
    field('name')
)

cabinet_serializer = serializer(
    field('id'),
    field('name'),
    child('datacenter', serializer=datacenter_embedded_serializer),
    field('rack_units'),
    field('depth'),
    field('width'),
    field('attachment', formatters=[enum_formatter()]),
    field('fasteners', formatters=[enum_formatter()])
)
