import requests
import os
from functions.download import get_invoice_path

url = 'https://adica.netlify.app/v2/validate'

def get_data(id):
    invoice_path = get_invoice_path(id)
    with open(invoice_path, 'rb') as file:
        return file.read()

def fetch_report(id):
    xml_data = get_data(id)
    headers = {'Content-Type': 'application/xml'}
    params = {
        "format": "html",
    }
    response = requests.post(url, headers=headers, data=xml_data, params=params)
    if not os.path.exists('static/Validation/'):
        os.makedirs('static/Validation/')
    with open(f'static/Validation/report{str(id)}.html', 'w') as file:
        file.write(response.text)

def display_report(id):
    with open(f'static/Validation/report{str(id)}.html', 'r') as file:
        data = file.read()
        return data

if __name__ == "__main__":
    fetch_report(1)
