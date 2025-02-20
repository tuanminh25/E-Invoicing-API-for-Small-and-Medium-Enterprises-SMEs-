#!/usr/bin/python3

import pytest
from server import app
from bs4 import BeautifulSoup
import os

# Extract the CSRF token from the response content
def extract_csrf_token(response):
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token_input = soup.find('input', {'name': 'csrf_token'})

    if csrf_token_input:
        return csrf_token_input['value']
    else:
        raise ValueError('CSRF token not found in the HTML response')

def extract_invoice_id(response):
    # Find the position of the start and end of the invoice ID within the HTML response
    start_index = response.data.find(b'Invoice ID:') + len(b'Invoice ID:')
    end_index = response.data.find(b'</p>', start_index)

    if start_index != -1 and end_index != -1:
        # Extract the invoice ID from the HTML response
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
        
def test_invoice_valid(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVValid.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVValid.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200   

def test_invoice_invalid_date(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVDateFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVDateFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_due_date_before_issue_date(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVDueBeforeIssueDate.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVDueBeforeIssueDate.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_quantity_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVInvoicedQuantityFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVInvoicedQuantityFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_extension_amount_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVInvoiceExtensionAmountFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVInvoiceExtensionAmountFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_name_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVItemNameFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVItemNameFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_missing_field_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVMissingField.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVMissingField.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_price_amount_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVPriceAmountFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVPriceAmountFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_extension_amount_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVProductExtensionAmountFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVProductExtensionAmountFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_tax_amount_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVTaxAmountFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVTaxAmountFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_file_type(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'png.png')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'png.png'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_due_date_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVDueDateFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVDueDateFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_payee_name_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVPayeeNameFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVPayeeNameFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_supplier_name_fail(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'CSV','CSVSupplierNameFail.csv')
    with open(test_file_path, 'rb') as f:
        csv_data = {'file': (f, 'CSVSupplierNameFail.csv'), 'csrf_token': csrf_token}
        response = client.post('/invoice/CSV', data=csv_data, content_type='multipart/form-data')

    assert response.status_code == 400