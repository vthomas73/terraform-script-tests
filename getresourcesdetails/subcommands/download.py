from utilities import logging, loading
from utilities import logging
import logging
import requests
import sys
import subprocess
sys.path.append('../utilities')
# from utilities import logging, loading
from utilities import logging, loading

logger = logging.get_logger(__name__)

PROVIDER_API_PROTOCOL = "https"
PROVIDERS_API_PATH = '/v1/providers'


def get_focused_provider_api_url(terraform_api_hostname, provider_name, provider_version):
    api_provider_path = '{}/{}/{}'.format(terraform_api_hostname,
                                          PROVIDERS_API_PATH, provider_name)
    api_full_path = '{}/{}'.format(api_provider_path,
                                   provider_version) if provider_version != 'latest' else api_provider_path
    api_full_path = api_full_path.replace('//', '/')
    return '{}://{}'.format(PROVIDER_API_PROTOCOL, api_full_path)


def clone_repository(repository_url, tag):
    logger.debug('provider source = {}'.format(repository_url))

    try:
        loader = loading.Loading(
            "Provider Downloading...", "Downloaded", 0.05).start()

        subprocess.check_output(["git", "clone", "--branch",
                                 tag, repository_url], stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as exc:
        loader.stop(output=False)
        logger.debug("Git clone failed : {}:{}".format(
            exc.returncode, exc.output))
        # print("Status : FAIL", exc.returncode, exc.output)
    else:
        loader.stop(output=True)
    # loader.stop(output = True)


def download(args):
    print(args)
    terraform_api_hostname = vars(args)['api_hostname']
    provider_resources_folder = vars(args)['provider_folder']

    provider_name = vars(args)['provider-name']
    provider_version = vars(args)['provider_version'] if vars(args)[
        'provider_version'] else ''

    api_url = get_focused_provider_api_url(
        terraform_api_hostname, provider_name, provider_version)
    logger.info('GET provider api {}'.format(api_url))

    r = requests.get(url=api_url)
    if r.status_code in [200, 404]:
        data = r.json()
        if 'errors' in data:
            logger.fatal('error during download, {}: {}'.format(
                r.status_code, data['errors'][0]))
                
        if 'version' in data and 'source' in data and 'tag' in data:
            logger.info(
                'provider found, going to download {}...'.format(data['tag']))
            clone_repository(str(data['source']), str(data['tag']))
