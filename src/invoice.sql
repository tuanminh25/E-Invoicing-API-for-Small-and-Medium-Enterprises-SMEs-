-- CREATE ROLE 'UserName' LOGIN PASSWORD 'Password';    -- Uncomment and change accordingly if you have yet to create your role
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;

CREATE TABLE Users (
    ID                              SERIAL PRIMARY KEY,
    UserName                        VARCHAR(20) UNIQUE, 
    Password                        VARCHAR(180)
);


CREATE TABLE Invoice (
    userID                          INT REFERENCES Users(ID),
    
    -- invoice
    ID                              SERIAL PRIMARY KEY,                             

    IssueDate                       TEXT NOT NULL,                                  -- cbc:IssueDate
    DueDate                         TEXT NOT NULL,                                  -- cbc:DueDate
    CHECK (IssueDate < DueDate),

    InvoiceTypeCode                 TEXT NOT NULL,                                  -- cbc:InvoiceTypeCode
    DocumentCurrencyCode            TEXT NOT NULL,                                  -- cbc:DocumentCurrencyCode

    -- supplier party contact point
    SupplierID                      BIGINT NOT NULL,
    SupplierEndpointID              BIGINT NOT NULL,
    SupplierName                    TEXT NOT NULL,                                  --cac:AccountingSupplierParty cac:Party cac:Contact cbc:Name
    -- postal address
    SupplierStreetName              TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:StreetName
    SupplierAdditionalStreetName    Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:AdditionalStreetName 
    SupplierCityName                Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:CityName            
    SupplierPostalZone              INT CHECK (SupplierPostalZone >= 0),            --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:PostalZone
    SupplierCountrySubentity        Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:CountrySubentity
    SupplierCountryCode             Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:IdentificationCode
    SupplierElectronicMail          TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cbc:ElectronicMail
    SupplierTelephone               TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cbc:Telephone
    -- supplier company registration
    SupplierCompany                 TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:PartyName cbc:Name

    -- payee party contact point
    PayeeID                         BIGINT NOT NULL,
    PayeeEndpointID                 BIGINT NOT NULL,
    PayeeName                       TEXT NOT NULL,                                  --cac:AccountingCustomerParty cac:Party cac:Contact cbc:Name
    -- postal address
    PayeeStreetName                 TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:StreetName
    PayeeAdditionalStreetName       Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:AdditionalStreetName 
    PayeeCityName                   Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:CityName            
    PayeePostalZone                 INT CHECK (PayeePostalZone >= 0),               --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:PostalZone
    PayeeCountrySubentity           Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:CountrySubentity
    PayeeCountryCode                Text,                                           --cac:AccountingSupplierParty cac:Party cac:Contact cac:PostalAddress cbc:IdentificationCode
    PayeeElectronicMail             TEXT,                                           --cac:AccountingCustomerParty cac:Party cac:Contact cbc:ElectronicMail
    PayeeTelephone                  TEXT,                                           --cac:AccountingCustomerParty cac:Party cac:Contact cbc:Telephone
    -- payee company registration
    PayeeCompany                    TEXT,                                           --cac:AccountingSupplierParty cac:Party cac:PartyName cbc:Name

    -- payment information
    LineExtensionAmount             NUMERIC CHECK (LineExtensionAmount >= 0),           -- cac:LegalMonetaryTotal cbc:LineExtensionAmount
    TaxAmount                       NUMERIC CHECK (TaxAmount >= 0),
    TaxableAmount                   NUMERIC CHECK (TaxableAmount >= 0),
    TaxCategoryId                   TEXT NOT NULL,
    TaxPercent                      NUMERIC CHECK (TaxPercent >= 0),
    TaxSchemeID                     TEXT NOT NULL,
    TaxExclusiveAmount              NUMERIC CHECK (TaxExclusiveAmount >= 0),
    TaxInclusiveAmount              NUMERIC CHECK (TaxInclusiveAmount >= 0),
    PayableRoundingAmount           NUMERIC CHECK (PayableRoundingAmount >= 0),
    PayableAmount                   NUMERIC CHECK (PayableAmount>= 0)
);

CREATE TABLE Product (
    pID                             SERIAL PRIMARY KEY,
    iID                             INT REFERENCES Invoice(ID) ON DELETE CASCADE,
    ItemName                        TEXT NOT NULL,                                  -- cac:InvoiceLine cac:Item cac:Name
    InvoicedQuantity                INT CHECK (InvoicedQuantity >= 0),              -- cbc:InvoicedQuantity

    -- Tax information
    TaxAmount                       NUMERIC CHECK (TaxAmount >= 0),                     -- cac:TaxTotal cbc:TaxPercent
    TaxSchemeID                     TEXT NOT NULL,                                  -- cac:ClassifiedTaxCategory
    ClassifiedTaxCategoryId         TEXT NOT NULL,

    -- payment information
    PriceAmount                     NUMERIC CHECK (PriceAmount >= 0),
    LineExtensionAmount             NUMERIC CHECK (LineExtensionAmount >= 0)
);
