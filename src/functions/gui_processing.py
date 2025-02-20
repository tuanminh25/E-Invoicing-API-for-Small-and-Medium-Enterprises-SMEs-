#!/usr/bin/python3

import psycopg2
from datetime import datetime
from functions.constants import addInvoiceQuery,addProductQuery, invoiceTableList, productTableList

def loadInvoice(formDict, invoiceList):
    for field in invoiceTableList:
        invoiceList.append(formDict[field] if formDict[field] else None)

    issue = datetime.strptime(invoiceList[1], '%Y-%m-%d')
    invoiceList[1] = issue.strftime('%d/%m/%Y')
    due = datetime.strptime(invoiceList[2], '%Y-%m-%d')
    invoiceList[2] = due.strftime('%d/%m/%Y')

    return invoiceList

def loadProduct(formDict, noProduct):
    if int(noProduct) > 0 and 'ItemName0' not in formDict:
        return []
    
    productList = []
    i = 0
    while i < int(noProduct):
        productEntry = []
        for (field) in productTableList:
            productEntry.append(formDict[field+str(i)] if formDict[field+str(i)] else None)
        productList.append(productEntry)
        i += 1
    return productList

def processGUI(formDict, userId):
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

    cur.execute(addInvoiceQuery, loadInvoice(formDict, [userId]))
    invoiceID = cur.fetchone()[0]

    products_data = loadProduct(formDict, formDict['numberOfItems'])
    print(products_data)

    for product in products_data:
      product.append(invoiceID)

    for product in products_data:
      if len(product) > 1:
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