#!/usr/bin/python3

import psycopg2
import os
import json
import pytest
from server import app
from bs4 import BeautifulSoup

def extract_csrf_token(response):
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token_input = soup.find('input', {'name': 'csrf_token'})

    if csrf_token_input:
        return csrf_token_input['value']
    else:
        raise ValueError('CSRF token not found in the HTML response')

def extract_invoice_id(response):
    start_index = response.data.find(b'Invoice ID:') + len(b'Invoice ID:')
    end_index = response.data.find(b'</p>', start_index)

    if start_index != -1 and end_index != -1:
        invoice_id = response.data[start_index:end_index].strip().decode('utf-8')
        return invoice_id
    else:
        raise ValueError('Invoice ID not found in the HTML response')

@pytest.fixture
def client():
    """Create a test client for the app."""
    with app.test_client() as client:
        response_get = client.get('/login')
        assert response_get.status_code == 200
        csrf_token = extract_csrf_token(response_get)
        login_response = client.post('/login', data=dict(
            csrf_token=csrf_token,
            username='test',
            password='testtest',
            submit='Login' 
        ), follow_redirects=True)
        assert login_response.status_code == 200
        assert login_response.request.path == '/'
        yield client

def test_invoice_update_due_date_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'DueDate', 
        'updatedValue': '25/12/2024',  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200   

def test_invoice_update_due_date_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'DueDate', 
        'updatedValue': '25/12/2022',  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_issue_date_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'IssueDate', 
        'updatedValue': '25/12/2022',  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_issue_date_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'IssueDate', 
        'updatedValue': '25/12/2026',  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200     

def test_invoice_update_due_date_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'DueDate', 
        'updatedValue': '25/12/2022',  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_supplier_name_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'SupplierName', 
        'updatedValue': "Supplier",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_supplier_name_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'SupplierName', 
        'updatedValue': "",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_payee_name_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'PayeeName', 
        'updatedValue': "John Fortnite",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_payee_name_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'PayeeName', 
        'updatedValue': "",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_payee_name_invalid_2(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'PayeeName', 
        'updatedValue': "None",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_line_extension_amount_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'LineExtensionAmount', 
        'updatedValue': 100,  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_line_extension_amount_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'LineExtensionAmount', 
        'updatedValue': -1,  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_multiple_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    update_data = {
        'fieldName': 'LineExtensionAmount', 
        'updatedValue': 100,  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    update_data = {
        'fieldName': 'PayeeName', 
        'updatedValue': "John Fortnite",  
        'productId': None  
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200
   
    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def extract_product_id(invoice_id):
    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )
    cur = db.cursor()

    cur.execute("SELECT pID FROM Product WHERE iID = %s", (invoice_id,))

    product_id = cur.fetchone()

    cur.close()
    db.close()

    return product_id[0]

def test_invoice_update_item_name_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'ItemName', 
        'updatedValue': "Robux",  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_item_name_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'ItemName', 
        'updatedValue': None,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_invoiced_quantity_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'InvoicedQuantity', 
        'updatedValue': 50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 


def test_invoice_update_invoiced_quantity_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'InvoicedQuantity', 
        'updatedValue': "-50",  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_tax_amount_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'TaxAmount', 
        'updatedValue': 50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_tax_amount_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'TaxAmount', 
        'updatedValue': -50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200

def test_invoice_update_price_amount_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'PriceAmount', 
        'updatedValue': 50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 
    
def test_invoice_update_price_amount_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'PriceAmount', 
        'updatedValue': -50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_product_line_extension_valid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'LineExtensionAmount', 
        'updatedValue': 50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

def test_invoice_update_product_line_extension_invalid(client):
    """Test the update/invoice/<id> route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200
    product_id = extract_product_id(invoice_id)

    update_data = {
        'fieldName': 'LineExtensionAmount', 
        'updatedValue': -50,  
        'productId': product_id
    }

    update_response = client.post(f'/update/invoice/{invoice_id}', json=update_data)
    assert update_response.status_code == 400

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 