#!/usr/bin/python3

import psycopg2
from datetime import datetime

def update(jsonResponse, invoice_id):

    fieldName = jsonResponse['fieldName']
    updatedValue = jsonResponse['updatedValue']
    product_id = jsonResponse['productId']

    updateInvoice = "UPDATE Invoice SET {} = %s WHERE ID = %s"
    updateInvoice = "UPDATE Invoice SET {} = %s WHERE ID = %s"
    updateProduct = "UPDATE Product SET {} = %s WHERE pID = %s"

    if updatedValue == "" or updatedValue == "None":
        updatedValue = None

    if fieldName in ['IssueDate', 'DueDate']:
        try:
            datetime.strptime(updatedValue, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Date format must be DD/MM/YYYY")

    try:
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )        
        cur = db.cursor()
        if product_id is None:
            if fieldName in ['IssueDate', 'DueDate']:
                updateInvoice = "UPDATE Invoice SET {} = TO_DATE(%s, 'DD/MM/YYYY') WHERE ID = %s"
            formatted_query = updateInvoice.format(fieldName)
            cur.execute(formatted_query, [updatedValue, invoice_id])
        else:
            formatted_query = updateProduct.format(fieldName)
            cur.execute(formatted_query, [updatedValue, product_id])
        db.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        if db:
            db.rollback()
            db.close()
        raise
