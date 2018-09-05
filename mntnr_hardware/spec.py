import os

from deepmerge import always_merger
import yaml


def get_spec(version):
    """
    Gets the OpenAPI schema and returns it as a python dictionary.

    :param version: version string, e.g. "v1"
    :return: dictionary object representing openapi schema
    :rtype: dict
    """
    here = os.path.dirname(os.path.realpath(__file__))
    spec_dir = os.path.join(here, 'api_{}'.format(version), 'specs')
    api_spec = {}
    for specfile in os.listdir(spec_dir):
        with open(os.path.join(spec_dir, specfile), 'rb') as specfo:
            spec = yaml.safe_load(specfo.read())
        api_spec = always_merger.merge(api_spec, spec)
    return api_spec
