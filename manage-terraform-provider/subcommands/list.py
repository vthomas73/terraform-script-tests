from utilities import logging, loading
import sys
import os
sys.path.append('../utilities')
from utilities import logging
# from utilities import logging

logger = logging.get_logger(__name__)


def fast_scandir(dirname):
    return [f.name for f in os.scandir(dirname) if f.is_dir()]


def list_cmd(args):
    provider_resources_folder = vars(args)['provider_folder']

    terraform_registries = fast_scandir(provider_resources_folder)
    if len(terraform_registries) == 0:
        logger.warning('no providers available. Use download command to get one')
    for tr in terraform_registries:
        logger.info('----- registry {} -----'.format(tr))
        groups = fast_scandir(os.path.join(provider_resources_folder, tr))
        for g in groups:
            packages = fast_scandir(os.path.join(
                provider_resources_folder, tr, g))
            for p in packages:
                versions = fast_scandir(os.path.join(
                provider_resources_folder, tr, g, p))
                # for v in versions:
                logger.info('provider {}/{} available, versions : {}'.format(g,p, versions))