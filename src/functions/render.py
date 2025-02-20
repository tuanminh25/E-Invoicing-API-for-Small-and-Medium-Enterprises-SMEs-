import requests
import json
import os
from functions.download import get_invoice_path

api_key = 'tYVcJbKciq9uXLGnTL6Oy6Cws9x4M0FE7F4WGY4B'
user_name = 'fiveguys1'
password = 'Fiveguys123!'

json_url = 'https://say9ms9h67.execute-api.ap-southeast-2.amazonaws.com/prod/api/render/json'
html_url = 'https://say9ms9h67.execute-api.ap-southeast-2.amazonaws.com/prod/api/render/html'

xml_pth = 'static/XMLFiles/'
rendered_pth = 'static/RenderedInvoice/'


def get_data(id):
    invoice_path = get_invoice_path(id)
    with open(invoice_path, 'r') as file:
        return file.read()


def fetch_api_json(id):
    xml_data = get_data(id)
    headers = {
        'Content-Type': 'text/xml',
        'x-api-key': api_key
    }

    response = requests.post(json_url, headers=headers, data=xml_data)

    if not os.path.exists(rendered_pth):
        os.makedirs(rendered_pth)
    pth = rendered_pth + str(id) + '.json'
    with open(pth, 'w') as file:
        data = json.dumps(response.json(), indent=4)
        file.write(data)


def fetch_api_html(id):
    xml_data = get_data(id)
    headers = {
        'Content-Type': 'text/xml',
        'x-api-key': api_key
    }

    response = requests.post(html_url, headers=headers, data=xml_data)

    if not os.path.exists(rendered_pth):
        os.makedirs(rendered_pth)
    pth = rendered_pth + str(id) + '.html'
    with open(pth, 'w') as file:
        file.write(response.text)


def display_json(id):
    with open(f'static/RenderedInvoice/{id}.json', 'r') as file:
        data = file.read()
        return data;


def display_html(id):
    with open(f'static/RenderedInvoice/{id}.html', 'r') as file:
        data = file.read()
        return data;


if __name__ == "__main__":
    fetch_api_html(20)
    fetch_api_json(20)
