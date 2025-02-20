#!/usr/bin/python3

import csv
import psycopg2
import os
from functions.constants import addInvoiceQuery,addProductQuery

def loadData(fileName, userId):
  global invoice_data, products_data
  invoice_data = []
  products_data = []
  invoice_data.append(userId)

  with open(fileName) as csvfile:
    data = csv.reader(csvfile, delimiter=',')

    for index,row in enumerate(data):
      non_empty_values = [cell for cell in row if cell != '']
      if index == 4 :
        for fields in non_empty_values:
          if fields == 'NULL':
              invoice_data.append(None)
          else:
            invoice_data.append(fields)
      elif index > 7:
        for i in range(len(non_empty_values)):
          if non_empty_values[i] == 'NULL':
              non_empty_values[i] = None
        products_data.append(non_empty_values)

    os.remove(fileName)
    return

def processCSV(fileName, userId):
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
