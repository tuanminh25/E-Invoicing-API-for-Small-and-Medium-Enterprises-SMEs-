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

def test_invoice_valid(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200   

def test_invoice_invalid_date(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONDateFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONDateFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_due_date_before_issue_date(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONDueBeforeIssueDate.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONDueBeforeIssueDate.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_quantity_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONInvoicedQuantityFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONInvoicedQuantityFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_invoice_extension_amount_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONInvoiceExtensionAmountFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONInvoiceExtensionAmountFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_name_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONItemNameFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONItemNameFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_missing_field_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONMissingField.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONMissingField.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_price_amount_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONPriceAmountFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONPriceAmountFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_extension_amount_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONProductExtensionAmountFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONProductExtensionAmountFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_product_tax_amount_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONTaxAmountFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONTaxAmountFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_file_type(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'png.png')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'png.png'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_due_date_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONDueDateFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONDueDateFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_payee_name_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONPayeeNameFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONPayeeNameFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400

def test_supplier_name_fail(client):
    """Test the /invoice/JSON route."""
    response_get = client.get('/invoice/JSON')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__), 'JSON','JSONSupplierNameFail.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONSupplierNameFail.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')

    assert response.status_code == 400