#!/usr/bin/python3

import json
import psycopg2
import os
from functions.constants import addInvoiceQuery,addProductQuery

def loadData(fileName, userId):
  global invoice_data, products_data
  invoice_data = []
  products_data = []

  with open(fileName, 'r') as file:
      data = json.load(file)

      for key, value in data['invoiceinfo'].items():
        invoice_data.append([key, value])
      for product in data['products']:
          product_info = []
          for key, value in product.items():
              product_info.append([key, value])
          products_data.append(product_info)

  invoice_data = [invoice_info[1] for invoice_info in invoice_data]
  invoice_data.insert(0, userId)
  products_data = [[subitem[1] for subitem in sublist] for sublist in products_data]
  os.remove(fileName)
  return


def processJSON(fileName, userId):
  db = None
  try:
    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )
    cur = db.cursor()
    loadData(fileName, userId)
  
    cur.execute(addInvoiceQuery, invoice_data)
    invoiceID = cur.fetchone()[0]

    for product in products_data:
      product.append(invoiceID)

    for product in products_data:
      cur.execute(addProductQuery, product)

    db.commit()
    return invoiceID

  except psycopg2.Error as db_error:
    if db:
      db.rollback()
    raise Exception(f"Database error: {db_error}")
  except Exception as err:
    # print(err)
    raise
  finally:
    if db:
      db.close()