import os
import yaml


def get_spec(version):
    """
    Gets the OpenAPI schema and returns it as a python dictionary.

    :param version: version string, e.g. "v1"
    :return: dictionary object representing openapi schema
    :rtype: dict
    """
    here = os.path.dirname(os.path.realpath(__file__))
    schema_file = os.path.join(here, 'api_{}'.format(version), 'openapi.yml')
    with open(schema_file, 'rb') as schema_fobj:
        schema = yaml.safe_load(schema_fobj)
    return schema