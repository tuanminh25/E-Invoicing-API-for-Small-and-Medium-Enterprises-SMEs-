import psycopg2
import os
import json
import pytest
from server import app
from bs4 import BeautifulSoup

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

def test_valid_delete(client):
    """Test the /clear/invoice/<int:id>."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)
    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id = extract_invoice_id(response)
    assert response.status_code == 200

    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )
    cur = db.cursor()

    cur.execute("select count(*) from Invoice where ID = %s",[invoice_id])
    count = cur.fetchone()[0]
    assert count == 1

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 200 

    cur.execute("select count(*) from Invoice where ID = %s",[invoice_id])
    count = cur.fetchone()[0]
    assert count == 0

def test_invalid_delete(client):
    """Test the /clear/invoice/<int:id>."""
    invoice_id = -5

    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )
    cur = db.cursor()
    cur.execute("select count(*) from Invoice where ID = %s",[invoice_id])
    count = cur.fetchone()[0]
    assert count == 0

    response_delete = client.delete(f'/clear/invoice/{invoice_id}')
    assert response_delete.status_code == 400 

    cur.execute("select count(*) from Invoice where ID = %s",[invoice_id])
    count = cur.fetchone()[0]
    assert count == 0

def test_invoice_valid(client):
    """Test the /invoice/CSV route."""
    response_get = client.get('/invoice/CSV')
    assert response_get.status_code == 200

    csrf_token = extract_csrf_token(response_get)

    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id1 = extract_invoice_id(response)
    assert response.status_code == 200

    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id2 = extract_invoice_id(response)
    assert response.status_code == 200

    test_file_path = os.path.join(os.path.dirname(__file__),'JSON','JSONValid.json')
    with open(test_file_path, 'rb') as f:
        json_data = {'file': (f, 'JSONValid.json'), 'csrf_token': csrf_token}
        response = client.post('/invoice/JSON', data=json_data, content_type='multipart/form-data')
    invoice_id3 = extract_invoice_id(response)
    assert response.status_code == 200

    response = client.get('/invoice')
    assert response.status_code == 200
    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )
    cur = db.cursor()
    cur.execute("SELECT id FROM invoice ORDER BY ID")
    data = [row[0] for row in cur.fetchall()]

    numbers_to_check = [invoice_id1, invoice_id2, invoice_id3]

    for number in numbers_to_check:
        assert int(number) in data   
        response_delete = client.delete(f'/clear/invoice/{int(number)}')
        assert response_delete.status_code == 200  
