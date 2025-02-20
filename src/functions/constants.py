CSVinstructions = (
    "// COPY THIS FORMAT AND CHANGE ACCORDINGLY,,,,,,,,,,,,\n"
    "// Replace 'NULL' or '0' with corresponding info,,,,,,,,,,,,\n"
    ",,,,,,,,,,,,\n"
    "IssueDate,DueDate,InvoiceTypeCode,DocumentCurrencyCode,SupplierID,SupplierEndpointID,SupplierName,SupplierStreetName,SupplierAdditionalStreetName,SupplierCityName,SupplierPostalZone,SupplierCountrySubentity,SupplierCountryCode,SupplierElectronicMail,SupplierTelephone,SupplierCompany,PayeeID,PayeeEndpointID,PayeeName,PayeeStreetName,PayeeAdditionalStreetName,PayeeCityName,PayeePostalZone,PayeeCountrySubentity,PayeeCountryCode,PayeeElectronicMail,PayeeTelephone,PayeeCompany,LineExtensionAmount,TaxAmount,TaxableAmount,TaxCategoryId,TaxPercent,TaxSchemeID,TaxExclusiveAmount,TaxInclusiveAmount,PayableRoundingAmount,PayableAmount\n"
    "DD/MM/YYYY,DD/MM/YYYY,71,AUD,0,0,NULL,NULL,NULL,NULL,0,NULL,AU,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,0,NULL,AU,NULL,NULL,NULL,0,0,0,S,0,GST,0,0,0,0\n"
    ",,,,,,,,,,,,\n"
    "// Write expenditure here with new instances on a new line\n"
    "ItemName,InvoicedQuantity,TaxAmount,TaxSchemeID,ClassifiedTaxCategoryId,PriceAmount,LineExtensionAmount\n"
    "NULL,0,0,GST,S,0,0,,,,,,,,\n"
)

JSONinstructions = (
""" {
    "invoiceinfo": {
        "IssueDate": "DD/MM/YYYY",
        "DueDate": "DD/MM/YYYY",
        "InvoiceTypeCode": 71,
        "DocumentCurrencyCode": "AUD",
        "SupplierID": 0,
        "SupplierEndpointID": 0
        "SupplierName": null,
        "SupplierStreetName": null,
        "SupplierAdditionalStreetName": null,
        "SupplierCityName": null,
        "SupplierPostalZone": 0,
        "SupplierCountrySubentity": null,
        "SupplierCountryCode": "AU",
        "SupplierElectronicMail": null,
        "SupplierTelephone": null,
        "SupplierCompany": null,
        "PayeeID": 1,
        "PayeeEndpointID": 0
        "PayeeName": null,
        "PayeeStreetName": null,
        "PayeeAdditionalStreetName": null,
        "PayeeCityName": null,
        "PayeePostalZone": 0,
        "PayeeCountrySubentity": null,
        "PayeeCountryCode": "AU",
        "PayeeElectronicMail": null,
        "PayeeTelephone": null,
        "PayeeCompany": null,
        "LineExtensionAmount": 0,
        "TaxAmount": 0,
        "TaxableAmount": 0,
        "TaxCategoryId": "S",
        "TaxPercent": 0,
        "TaxSchemeID": "GST",
        "TaxExclusiveAmount": 0,
        "TaxInclusiveAmount": 0,
        "PayableRoundingAmount": 0,
        "PayableAmount": 0
    },
    "products": [
        {
            "ItemName": null,
            "InvoicedQuantity": 0,
            "TaxAmount": 0,
            "TaxSchemeID": "GST",
            "ClassifiedTaxCategoryId": "S",
            "PriceAmount": 0,
            "LineExtensionAmount": 0
        }
    ]
} """
)

addInvoiceQuery = f"""
  INSERT INTO Invoice (
    userID,
    IssueDate,
    DueDate,
    InvoiceTypeCode,
    DocumentCurrencyCode,
    SupplierID,
    SupplierEndpointID,
    SupplierName,
    SupplierStreetName,
    SupplierAdditionalStreetName,
    SupplierCityName,
    SupplierPostalZone,
    SupplierCountrySubentity,
    SupplierCountryCode,
    SupplierElectronicMail,
    SupplierTelephone,
    SupplierCompany,
    PayeeID,
    PayeeEndpointID,
    PayeeName,
    PayeeStreetName,
    PayeeAdditionalStreetName,
    PayeeCityName,
    PayeePostalZone,
    PayeeCountrySubentity,
    PayeeCountryCode,
    PayeeElectronicMail,
    PayeeTelephone,
    PayeeCompany,
    LineExtensionAmount,
    TaxAmount,
    TaxableAmount,
    TaxCategoryId,
    TaxPercent,
    TaxSchemeID,
    TaxExclusiveAmount,
    TaxInclusiveAmount,
    PayableRoundingAmount,
    PayableAmount
  )
  VALUES (
     %s, TO_DATE(%s, 'DD/MM/YYYY'), TO_DATE(%s, 'DD/MM/YYYY'),
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
  RETURNING ID;
"""

addProductQuery = f"""
  INSERT INTO Product (
    ItemName,
    InvoicedQuantity,
    TaxAmount,
    TaxSchemeID,
    ClassifiedTaxCategoryId,
    PriceAmount,
    LineExtensionAmount,
    iID
  )
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

addUserQuery = f"""
  INSERT INTO Users (
    UserName,
    Password
  )
  VALUES (%s,%s);
"""

invoiceTableList = ["IssueDate","DueDate","InvoiceTypeCode","DocumentCurrencyCode","SupplierID","SupplierEndpointID","SupplierName","SupplierStreetName","SupplierAdditionalStreetName","SupplierCityName","SupplierPostalZone","SupplierCountrySubentity","SupplierCountryCode","SupplierElectronicMail","SupplierTelephone","SupplierCompany","PayeeID","PayeeEndpointID","PayeeName","PayeeStreetName","PayeeAdditionalStreetName","PayeeCityName","PayeePostalZone","PayeeCountrySubentity","PayeeCountryCode","PayeeElectronicMail","PayeeTelephone","PayeeCompany","LineExtensionAmount","TaxAmount","TaxableAmount","TaxCategoryId","TaxPercent","TaxSchemeID","TaxExclusiveAmount","TaxInclusiveAmount","PayableRoundingAmount","PayableAmount"]
productTableList = ["ItemName","InvoicedQuantity","TaxAmount","TaxSchemeID","ClassifiedTaxCategoryId","PriceAmount","LineExtensionAmount"]
