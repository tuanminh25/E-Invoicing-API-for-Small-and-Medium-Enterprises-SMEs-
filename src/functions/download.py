xml_pth = 'static/XMLFiles/'

def get_invoice_path(id):
    invoice_path = xml_pth + str(id) + '.xml'
    return invoice_path

def get_format_path(format):
    format_path = f"static/{format}_format.{format}"
    return format_path