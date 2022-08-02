import os
import re

RESOURCES_PATH = '../../resources/'
AWS_PATH = "terraform-provider-aws/"
AZURE_PATH = "terraform-provider-azurerm/"
GCP_PATH = "terraform-provider-google/"
PROVIDER_DOC_PATH = "website/docs/r/"


class ResourceDetails:
    def __init__(self, resource_name, attributes_details, outputs_details) -> None:
        self.name = resource_name
        self.attributes = attributes_details
        self.outputs = outputs_details

    def print_description(self):
        print("Resource = {}".format(self.name))
        for attr in self.attributes:
            attr.print_description()
        for out in self.outputs:
            out.print_description()


class OutputDetails:
    def __init__(self, name, description) -> None:
        self.name = name
        self.description = description

    def print_description(self):
        print("Name = {}, description = {}".format(
            self.name, self.description))


class AttributeDetails:
    def __init__(self, name, required, description) -> None:
        self.name = name
        self.required = required
        self.description = description

    def print_description(self):
        print("Name = {}, required = {}, description = {}".format(
            self.name, self.required, self.description))


def get_resource_name(file_path):
    regex = r"^# Resource: (?P<resource_name>\w*)$"
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for l in lines:
            result = re.search(regex, l)
            if result:
                return result.group('resource_name')


def get_arguments(file_path):
    regex = r"\* `(?P<variable_name>.*)` - \((?P<is_optional>\w*)\) (?P<description>(?:.|\n)*?(?=\n\*|$))"
    attrs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for l in lines:
            result = re.search(regex, l)
            if result:
                attr = AttributeDetails(result.group('variable_name'), True if result.group(
                    'is_optional') == "Required" else False, result.group('description'))
                attrs.append(attr)
    return attrs

def get_outputs(file_path):
    regex = r"\* `(?P<output_name>.*)` - (?P<description>(?:.|\n)*?(?=\n\*|$))"
    attrs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for l in lines:
            result = re.search(regex, l)
            if result:
                attr = OutputDetails(result.group(
                    'output_name'), result.group('description'))
                attrs.append(attr)
    return attrs


def get_resources_details(doc_path):
    provider_resources_details = []
    for file in os.listdir(doc_path):
        if file.endswith(".markdown"):
            path = os.path.join(doc_path, file)
            resource_name = get_resource_name(path)
            attrs = get_arguments(path)
            outputs = get_outputs(path)
            provider_resources_details.append(
                ResourceDetails(resource_name, attrs, outputs))
    return provider_resources_details


aws_resources_details = get_resources_details(
    os.path.join(RESOURCES_PATH, AWS_PATH, PROVIDER_DOC_PATH))
azure_resources_details = get_resources_details(
    os.path.join(RESOURCES_PATH, AZURE_PATH, PROVIDER_DOC_PATH))
gcp_resources_details = get_resources_details(
    os.path.join(RESOURCES_PATH, GCP_PATH, PROVIDER_DOC_PATH))


print('Resources trouvées : {}'.format(len(aws_resources_details)))
print('Resources trouvées : {}'.format(len(azure_resources_details)))
print('Resources trouvées : {}'.format(len(gcp_resources_details)))
