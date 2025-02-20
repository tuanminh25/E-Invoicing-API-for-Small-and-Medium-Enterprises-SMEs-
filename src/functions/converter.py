#!/usr/bin/python3

import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys
import psycopg2
import traceback

db = None

qry_invoice = """
    select {} from Invoice
    where ID = %s;
"""

qry_product = """
    select {} from Product
    where pID = %s;
"""

list_products = f"""
    select pID from Product p
    where p.iID = %s;
"""

placeholder = 'something'

def get_invoice(fname, invoice_id, cur):
    formatted_query = qry_invoice.format(fname)
    cur.execute(formatted_query, [invoice_id])
    res = cur.fetchall()
    return res[0][0]

def get_product(fname, product_id, cur):
    formatted_query = qry_product.format(fname)
    cur.execute(formatted_query, [product_id])
    res = cur.fetchall()
    return res[0][0]

def list_productsID(invoice_id, cur):
    cur.execute(list_products , [invoice_id])
    res = cur.fetchall()
    return res

def createCac(parent, name):
    element = ET.SubElement(parent, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}cac:'+name)
    return element

def addCbc(parent, name, text, **attrib):
    ET.SubElement(parent, 'cbc:'+name, attrib).text = text

def remove_namespace_prefixes(elem):
    elem.tag = elem.tag.split('}')[-1]
    for child in elem:
        remove_namespace_prefixes(child)

def convert_int_to_str(element):
    for child in element:
        convert_int_to_str(child)

        try:
            int_value = int(child.text)
            child.text = str(int_value)
        except (TypeError, ValueError):
            pass

def create_party(invoice, invoice_id, cur, party_type):
    party_id = str(get_invoice(party_type + "ID", invoice_id, cur))
    endpoint_id = str(get_invoice(party_type + "EndpointID", invoice_id, cur))
    name = get_invoice(party_type + "Name", invoice_id, cur)
    street_name = get_invoice(party_type + "StreetName", invoice_id, cur) if get_invoice(party_type + "StreetName", invoice_id, cur) is not None else "Street Name N/A"
    add_street_name = get_invoice(party_type + "AdditionalStreetName", invoice_id, cur) if get_invoice(party_type + "AdditionalStreetName", invoice_id, cur) is not None else ""
    city_name = get_invoice(party_type + "CityName", invoice_id, cur) if get_invoice(party_type + "CityName", invoice_id, cur) is not None else "City Name N/A"
    postal_zone = str(get_invoice(party_type + "PostalZone", invoice_id, cur))
    country_sub_entity = get_invoice(party_type + "CountrySubentity", invoice_id, cur) if get_invoice(party_type + "CountrySubentity", invoice_id, cur) is not None else "Country Subentity N/A"
    country_code = get_invoice(party_type + "CountryCode", invoice_id, cur) if get_invoice(party_type + "CountryCode", invoice_id, cur) is not None else "Country Code N/A"
    electronic_mail = get_invoice(party_type + "ElectronicMail", invoice_id, cur) if get_invoice(party_type + "ElectronicMail", invoice_id, cur) is not None else "Electronic Mail N/A"
    telephone = get_invoice(party_type + "Telephone", invoice_id, cur) if get_invoice(party_type + "Telephone", invoice_id, cur) is not None else "Telephone N/A"
    company = get_invoice(party_type + "Company", invoice_id, cur) if get_invoice(party_type + "Company", invoice_id, cur) is not None else "Company N/A"
    tax_scheme_id = get_invoice('TaxSchemeID', invoice_id, cur)

    accounting_name = 'AccountingSupplierParty'

    if party_type == 'Payee':
        accounting_name = 'AccountingCustomerParty'

    if add_street_name is None:
        add_street_name = ''

    accounting_party = createCac(invoice, accounting_name)
    party = createCac(accounting_party, 'Party')
    addCbc(party, 'EndpointID', endpoint_id, schemeID = '0151')
    party_identification = createCac(party, 'PartyIdentification')
    addCbc(party_identification, 'ID', party_id)

    party_name = createCac(party, 'PartyName')
    addCbc(party_name, 'Name', company)

    postal_address = createCac(party, 'PostalAddress')
    addCbc(postal_address, 'StreetName', street_name)
    if len(add_street_name) != 0:
        addCbc(postal_address, 'AdditionalStreetName', add_street_name)
    addCbc(postal_address, 'CityName', city_name)
    addCbc(postal_address, 'PostalZone', postal_zone)

    country = createCac(postal_address, 'Country')
    addCbc(country, 'IdentificationCode', country_code)

    tax_scheme = createCac(party, 'PartyTaxScheme')
    addCbc(tax_scheme, 'CompanyID', party_id)
    sub_tax_scheme = createCac(tax_scheme, 'TaxScheme')
    addCbc(sub_tax_scheme, 'ID', tax_scheme_id)

    party_legal_entity = createCac(party, 'PartyLegalEntity')
    addCbc(party_legal_entity, 'RegistrationName', company)
    addCbc(party_legal_entity, 'CompanyID', party_id, schemeID = "0151")

    contact = createCac(party, 'Contact')
    addCbc(contact, 'Name', name)
    addCbc(contact, 'Telephone', telephone)
    addCbc(contact, 'ElectronicMail', electronic_mail)

def create_product(invoice, pID, ItemName, InvoicedQuantity, TaxAmount, PriceAmount, LineExtensionAmount):
    InvoiceLine = createCac(invoice, 'InvoiceLine')
    addCbc(InvoiceLine, 'ID', pID)
    addCbc(InvoiceLine, 'InvoicedQuantity', InvoicedQuantity, unitCode="C62")
    addCbc(InvoiceLine, 'LineExtensionAmount', LineExtensionAmount, currencyID="AUD")

    Item = createCac(InvoiceLine, 'Item')
    addCbc(Item, 'Name', ItemName)

    ClassifiedTaxCategory = createCac(Item, 'ClassifiedTaxCategory')
    addCbc(ClassifiedTaxCategory, 'ID', 'S')
    addCbc(ClassifiedTaxCategory, 'Percent', TaxAmount)

    TaxScheme = createCac(ClassifiedTaxCategory, 'TaxScheme')
    addCbc(TaxScheme, 'ID', 'GST', schemeID="UN/ECE 5153")

    Price = createCac(InvoiceLine, 'Price')
    addCbc(Price, 'PriceAmount', PriceAmount, currencyID="AUD")
    addCbc(Price, 'BaseQuantity', '1.0', unitCode="C62")

def create_tax(invoice, invoice_id, cur, currency_code):
    tax_amount = str("{:.2f}".format(get_invoice("TaxAmount", invoice_id, cur)))
    taxable_amount = str("{:.2f}".format(get_invoice("TaxableAmount", invoice_id, cur)))
    tax_category_id = str(get_invoice("TaxCategoryId", invoice_id, cur))
    tax_percent = str("{:.2f}".format(get_invoice("TaxPercent", invoice_id, cur)))
    tax_scheme_id = str(get_invoice("TaxSchemeID", invoice_id, cur))

    TaxTotal = createCac(invoice, 'TaxTotal')
    addCbc(TaxTotal, 'TaxAmount', tax_amount,  currencyID=currency_code)
    TaxSubtotal = createCac(TaxTotal, 'TaxSubtotal')
    addCbc(TaxSubtotal, 'TaxableAmount', taxable_amount,  currencyID=currency_code)
    addCbc(TaxSubtotal, 'TaxAmount', tax_amount,  currencyID=currency_code)
    TaxCategory = createCac(TaxSubtotal, 'TaxCategory')
    addCbc(TaxCategory, 'ID', tax_category_id)
    addCbc(TaxCategory, 'Percent', tax_percent)
    TaxScheme = createCac(TaxCategory, 'TaxScheme')
    addCbc(TaxScheme, 'ID', tax_scheme_id)

def create_payment(invoice, invoice_id, cur, currency_code):
    line_extension_amount = str("{:.2f}".format(get_invoice("LineExtensionAmount", invoice_id, cur)))
    tax_exclusive_amount = str("{:.2f}".format(get_invoice("TaxExclusiveAmount", invoice_id, cur)))
    tax_inclusive_amount = str("{:.2f}".format(get_invoice("TaxInclusiveAmount", invoice_id, cur)))
    payable_rounding_amount = str("{:.2f}".format(get_invoice("PayableRoundingAmount", invoice_id, cur)))
    payable_amount = str("{:.2f}".format(get_invoice("PayableAmount", invoice_id, cur)))

    LegalMonetaryTotal = createCac(invoice, 'LegalMonetaryTotal')
    addCbc(LegalMonetaryTotal, 'LineExtensionAmount', line_extension_amount, currencyID=currency_code)
    addCbc(LegalMonetaryTotal, 'TaxExclusiveAmount', tax_exclusive_amount, currencyID=currency_code)
    addCbc(LegalMonetaryTotal, 'TaxInclusiveAmount', tax_inclusive_amount, currencyID=currency_code)
    addCbc(LegalMonetaryTotal, 'PayableRoundingAmount', payable_rounding_amount, currencyID=currency_code)
    addCbc(LegalMonetaryTotal, 'PayableAmount', payable_amount, currencyID=currency_code)

def toXml(invoice_id):
    try:
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )       
        cur = db.cursor()

        invoice = ET.Element('{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice', attrib={
        'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'xmlns:cec': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
        })

        issue_date = get_invoice("IssueDate", invoice_id, cur)
        due_date = get_invoice("DueDate", invoice_id, cur)
        customizatio_id = 'urn:cen.eu:en16931:2017#conformant#urn:fdc:peppol.eu:2017:poacc:billing:international:aunz:3.0'
        profile_id = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'
        invoice_type_code = get_invoice("InvoiceTypeCode", invoice_id, cur)
        currency_code = get_invoice("DocumentCurrencyCode", invoice_id, cur)

        addCbc(invoice, 'UBLVersionID', '2.1')
        addCbc(invoice, 'CustomizationID', customizatio_id)
        addCbc(invoice, 'ProfileID', profile_id)
        addCbc(invoice, 'ID', str(invoice_id))
        addCbc(invoice, 'IssueDate', str(issue_date))
        addCbc(invoice, 'DueDate', str(due_date))
        addCbc(invoice, 'InvoiceTypeCode', invoice_type_code)
        addCbc(invoice, 'DocumentCurrencyCode', currency_code)
        addCbc(invoice, 'BuyerReference', str(invoice_id))

        addition_doc_ref = createCac(invoice, 'AdditionalDocumentReference')
        addCbc(addition_doc_ref, 'ID', str(invoice_id))

        ###########################
        #        SUPPLIER         #
        ###########################

        create_party(invoice, invoice_id, cur, 'Supplier')
        create_party(invoice, invoice_id, cur, 'Payee')

        ###################################
        #          PAYMENT MEANS          #
        ###################################

        PaymentMeans = createCac(invoice, 'PaymentMeans')
        addCbc(PaymentMeans, 'PaymentMeansCode', '1')
        addCbc(PaymentMeans, 'PaymentID', str(invoice_id))

        PaymentTerms = createCac(invoice, 'PaymentTerms')
        addCbc(PaymentTerms, 'Note', 'As agreed')

        #########################
        #          TAX          #
        #########################

        create_tax(invoice, invoice_id, cur, currency_code)

        #############################
        #          PAYMENT          #
        #############################

        create_payment(invoice, invoice_id, cur, currency_code)

        ##############################
        #          PRODUCTS          #
        ##############################

        pids = list_productsID(invoice_id, cur)
        pids = [value for tpl in pids for value in tpl]

        if len(pids) != 0:
            for pid in pids:
                ItemName = get_product("ItemName", pid, cur)
                InvoicedQuantity = get_product("InvoicedQuantity", pid, cur)
                TaxAmount = "{:.2f}".format(get_product("TaxAmount", pid, cur))
                PriceAmount = "{:.2f}".format(get_product("PriceAmount", pid, cur))
                LineExtensionAmount = "{:.2f}".format(get_product("LineExtensionAmount", pid, cur))

                create_product(invoice, pid, ItemName, InvoicedQuantity, TaxAmount, PriceAmount, LineExtensionAmount)

        with open(f'static/XMLFiles/{str(invoice_id)}.xml', 'wb') as f:
            remove_namespace_prefixes(invoice)
            convert_int_to_str(invoice)
            invoiceString = ET.tostring(invoice, encoding='utf-8', xml_declaration=True)
            dom = xml.dom.minidom.parseString(invoiceString)
            prettified_xml_str = dom.toprettyxml(indent='  ')
            prettified_xml_str = str(prettified_xml_str)
            f.write(prettified_xml_str.encode('utf-8'))

    except Exception as err:
        print(traceback.format_exc())
        print("ERROR: ", err)
    finally:
        if db:
            db.close()
