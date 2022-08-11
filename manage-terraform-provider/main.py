import argparse
from utilities import logging
import subcommands

RESOURCES_PATH = '../../resources/'
AWS_PATH = "terraform-provider-aws/"
AZURE_PATH = "terraform-provider-azurerm/"
GCP_PATH = "terraform-provider-google/"
PROVIDER_DOC_PATH = "website/docs/r/"

logger = logging.get_logger(__name__)


def dowload_provider(args):
    print("dowload_provider" + str(args))


def get_provider_details(args):
    print("get_provider_details" + str(args))


def list_providers(args):
    print("list_providers" + str(args))


def cli():
    parser = argparse.ArgumentParser(
        description='Manage terraform providers and their resources')
    subparsers = parser.add_subparsers(
        title='Download, get or list providers',
        metavar='command')

    parser.add_argument(
        '--provider-folder', default='./resources',
        help='providers resource folder')

    dowload_parser = subparsers.add_parser(
        'download',
        help='Download provider')
    dowload_parser.add_argument(
        'provider-name',
        help='provider name to download. Ex: hashicorp/aws')
    dowload_parser.add_argument(
        '--api-hostname', default='registry.terraform.io',
        help='terraform registry url')
    dowload_parser.add_argument(
        '--provider-version', default='latest',
        help='provider version to download. Ex: 4.25.0')
    dowload_parser.set_defaults(handle=subcommands.download_cmd)

    get_parser = subparsers.add_parser(
        'get',
        help='Get provider details')
    get_parser.add_argument(
        'provider',
        help='provider to download')
    get_parser.set_defaults(handle=subcommands.get_cmd)

    list_parser = subparsers.add_parser(
        'list', aliases=['ls'],
        help='List providers')
    list_parser.set_defaults(handle=subcommands.list_cmd)

    parser.parse_args()
    args = parser.parse_args()
    if not hasattr(args, 'handle'):
        parser.print_help()
    else:
        args.handle(args)


if __name__ == "__main__":
    cli()
