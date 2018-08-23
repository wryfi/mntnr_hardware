from strainer import (serializer, field, formatters, validators, ValidationException)


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
