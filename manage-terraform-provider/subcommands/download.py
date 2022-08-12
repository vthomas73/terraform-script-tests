import traceback
import json
from jinja2 import Template
import shutil
from typing import final
from utilities import logging, loading
from utilities import logging
import requests
import sys
import subprocess
import os
import shutil
import re
from pathlib import Path
from .constants import *
sys.path.append('../utilities')
from utilities import logging, loading
# from utilities import logging, loading

logger = logging.get_logger(__name__)

PROVIDER_API_PROTOCOL = "https"
PROVIDERS_API_PATH = '/v1/providers'
TEMPLATES_FOLDER = '{}/resources/templates/'.format(Path(__file__).parent)


def get_focused_provider_api_url(terraform_api_hostname, provider_name, provider_version):
    api_provider_path = '{}/{}/{}'.format(terraform_api_hostname,
                                          PROVIDERS_API_PATH, provider_name)
    api_full_path = '{}/{}'.format(api_provider_path,
                                   provider_version) if provider_version != 'latest' else api_provider_path
    api_full_path = api_full_path.replace('//', '/')
    return '{}://{}'.format(PROVIDER_API_PROTOCOL, api_full_path)


def produce_provider_file(provider_name, provider_version, provider_alias, provider_path):

    logger.debug('going to template {} file'.format(
        TEMPLATES_FOLDER + PROVIDER_TF_TEMPLATE_FILE))
    with open(TEMPLATES_FOLDER + PROVIDER_TF_TEMPLATE_FILE) as file_:
        template = Template(file_.read())
        rendered = template.render(provider_alias=provider_alias,
                                   provider_name=provider_name, provider_version=provider_version)

    with open('{}/{}'.format(provider_path, PROVIDER_TF_TEMPLATE_FILE), 'w') as f:
        f.write(rendered)


def get_description_recursively(obj, workdir, fileContent=None):
    description_regex = '\*\s*\x60attribute_name\x60\s*-\s*(?:\((\w*)\))?\s*(?P<description>(?:.|\n)*?(?P<line_break>(?:\n\*|$)))'

    for i in obj:  # name
        md_content = fileContent
        if not md_content:
            try:
                with open(os.path.join(workdir, '{}.markdown'.format(i)), 'r') as md:
                    md_content = md.read()
            except Exception as e:
                logger.warning(e)
                pass
        if 'attributes' in obj[i]['block']:
            for attr in obj[i]['block']['attributes']:
                logger.debug('attribute {} in  '.format(attr, i))
                res = re.search(description_regex.replace(
                    'attribute_name', attr), str(md_content), re.MULTILINE)
                if res:
                    description = res.group('description')
                    line_break = res.group('line_break')
                    formatted_description = description.replace(line_break, '')
                    logger.debug('attribute {} has description {}'.format(
                        attr, formatted_description))
                    obj[i]['block']['attributes'][attr]['description'] = formatted_description
        if 'block_types' in obj[i]['block']:
            logger.debug('{} has block_types'.format(i))
            obj[i]['block']['block_types'] = get_description_recursively(
                obj[i]['block']['block_types'], workdir, md_content)
    return obj


def add_data_description(workdir, data_file_name=PROVIDER_DATA_FILE):
    try:
        with open(os.path.join(workdir, data_file_name), 'r') as data_file:
            data_basis = json.load(data_file)

        provider_schemas = data_basis['provider_schemas']
        resource_schemas = provider_schemas[next(
            iter(provider_schemas))]['resource_schemas']
        data_source_schemas = provider_schemas[next(
            iter(provider_schemas))]['data_source_schemas']

        resource_schemas = get_description_recursively(
            resource_schemas, os.path.join(workdir, PROVDER_MARKDOWN_FOLDER, 'r/'))
        data_source_schemas = get_description_recursively(
            data_source_schemas, os.path.join(workdir, PROVDER_MARKDOWN_FOLDER, 'd/'))

        with open(os.path.join(workdir, 'resources.json'), "w") as outfile:
            outfile.write(json.dumps(resource_schemas))
        with open(os.path.join(workdir, 'data.json'), "w") as outfile:
            outfile.write(json.dumps(data_source_schemas))

        text_file = open(os.path.join(workdir, 'resources_schemas.json'), "w")
        text_file.write(json.dumps(provider_schemas))
        text_file.close()

    except Exception as e:
        logger.warning(e)
        pass

    # print(resources_schemas)


def provider_schema_exportation(workdir, terraform_data_file_name=PROVIDER_DATA_FILE):
    try:
        loader = loading.Loading(
            "Terraform is importing provider...", "Initialized", 0.05).start()
        subprocess.check_call(['terraform', 'init'], cwd=workdir,
                              stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        loader.stop(output=True)
        loader = loading.Loading(
            "Schema exportation...", "Exported", 0.05).start()
        with open('{}/{}'.format(workdir, terraform_data_file_name), "w") as outfile:
            subprocess.check_call(['terraform', 'providers', 'schema', '-json'],
                                  cwd=workdir, stderr=subprocess.STDOUT, stdout=outfile)
        
    except subprocess.CalledProcessError as exc:
        loader.stop(output=False)
    else:
        loader.stop(output=True)


def download_provider_documentation(repository_url, tag, target_folder, temporary_folder='tmp'):
    logger.info('going to download {}...'.format(tag))
    logger.debug('provider source = {}'.format(repository_url))

    os.makedirs(temporary_folder, exist_ok=True)

    try:
        loader = loading.Loading(
            "Provider Downloading...", "Downloaded", 0.05).start()

        subprocess.check_output(["git", "clone", "--branch",
                                 tag, repository_url, temporary_folder], stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError as exc:
        loader.stop(output=False)
        logger.debug("Git clone failed : {}:{}".format(
            exc.returncode, exc.output))
    else:
        loader.stop(output=True)
        logger.debug("downloaded, going to move {} to {}".format(
            temporary_folder, target_folder))
        markdown_full_path = os.path.join(
            target_folder, PROVDER_MARKDOWN_FOLDER)
        os.makedirs(markdown_full_path, exist_ok=True)

        resource_regex = '^#(?:\s.*)?\s(\S+)$'
        for path in Path(temporary_folder).rglob('*.markdown'):
            resource_type = 'r' if '/r/' in str(
                path.resolve()) else 'd' if '/d/' in str(path.resolve()) else 'unknown'
            resource_type_full_path = os.path.join(
                markdown_full_path, resource_type)

            os.makedirs(resource_type_full_path, exist_ok=True)
            try:
                with open(path.absolute(), "r") as md_file:
                    res = re.search(
                        resource_regex, md_file.read(), re.MULTILINE)
                    if res:
                        shutil.copy(path.absolute(), os.path.join(
                            resource_type_full_path, '{}.markdown'.format(res.group(1).replace('\\', ''))))
            except Exception as e:
                logger.warning(e)

        logger.info("Provider documentation downloaded")

    finally:
        logger.debug('going to delete {} folder'.format(temporary_folder))
        shutil.rmtree(temporary_folder)


def download_cmd(args):
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

        if 'id' in data and 'version' in data and 'source' in data and 'tag' in data:
            logger.info(
                'provider found')
            try:
                full_path = os.path.join(provider_resources_folder, terraform_api_hostname,
                                         provider_name, provider_version)
                provider_alias = provider_name.split('/')[-1]
                if not os.path.isdir(full_path):
                    download_provider_documentation(str(data['source']), str(
                        data['tag']), full_path, './tmp/download')
                    # produce_provider_data(provider_name, provider_version, provider_alias, full_path)
                else:
                    logger.info('provider {} {} already exists : {}'.format(
                        provider_name, data['tag'], full_path))
                if not os.path.isfile(os.path.join(full_path, PROVIDER_TF_TEMPLATE_FILE)):
                    produce_provider_file(
                        provider_name, provider_version, provider_alias, full_path)
                # if not os.path.join(full_path, PROVIDER_DATA_FILE):
                    provider_schema_exportation(full_path)
                    add_data_description(full_path)
            except OSError as err:
                logger.fatal(err)
