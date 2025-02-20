from flask import Flask, render_template_string, request, render_template, jsonify, redirect, url_for, send_file, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import binascii
import json
import psycopg2
import os
from functions.render import fetch_api_json, fetch_api_html, display_json, display_html
from functions.constants import CSVinstructions, JSONinstructions, addUserQuery
from functions.download import get_invoice_path, get_format_path
from functions.validate import fetch_report, display_report
from functions.json_processing import processJSON
from functions.csv_processing import processCSV
from functions.gui_processing import processGUI
from functions.update_invoice import update
from functions.converter import toXml

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'secretkey'
app.config['CSVFiles'] = 'static/CSVFiles'
app.config['JSONFiles'] = 'static/JSONFiles'

class PermissionError(Exception):
  def __init__(self, message="Permission Error"):
    self.message = message
    super().__init__(self.message)

class ExistenceError(Exception):
  def __init__(self, message="Permission Error"):
    self.message = message
    super().__init__(self.message)

def accessCheck(userId, fileId):
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

    cur.execute("SELECT COUNT(*) FROM Invoice WHERE ID = %s", [fileId])
    if (cur.fetchone()[0] == 0):
      raise ExistenceError("Invalid id: Invoice doesn't exist")

    cur.execute("SELECT COUNT(*) FROM Invoice WHERE userID = %s AND ID = %s", [userId, fileId])
    if (cur.fetchone()[0] == 0):
      raise PermissionError("Permission denied: Invoice doesn't belong to you")

  except PermissionError as pe:
    raise
  except ExistenceError as ee:
    raise
  finally:
    if db:
      db.close()

class CSVFile(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

class JSONFile(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )        
        cur = db.cursor()
        cur.execute("SELECT count(*) FROM Users where UserName=%s",[username.data])
        existing_user_username = cur.fetchone()[0]
        if existing_user_username > 0:
            db.close()
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        db.close()

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )        
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM Users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        db.close()
        if user_data:
            return User(*user_data)
        return None

    @staticmethod
    def get_by_username(username):
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )        
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM Users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        db.close()
        if user_data:
            return User(*user_data)
        return None

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/', methods = ['GET', 'POST'])
@login_required
def dashboard():
    return render_template('main.html')

@app.route('/invoice/CSV', methods = ['GET', 'POST'])
@login_required
def create_invoice_CSV():
    form = CSVFile()
    invoiceID = None
    try:
        if (form.validate_on_submit()):
            file = form.file.data
            if not os.path.exists('static/'):
                os.makedirs('static/')
            file.save(app.config['CSVFiles'] + file.filename)
            invoiceID = processCSV(app.config['CSVFiles'] + file.filename, current_user.id)
            if not os.path.exists('static/XMLFiles/'):
                os.makedirs('static/XMLFiles/')
            toXml(invoiceID)
    except UnicodeDecodeError as decode_error:
        os.remove(app.config['CSVFiles'] + file.filename)
        error_message = f"The file {file.filename} is not a valid CSV file."
        return render_template('error.html', error_message=error_message, status=0), 400
    except Exception as error:
        error_message = str(error)
        return render_template('error.html', error_message=error_message, status=0), 400

    return render_template('index.html', form = form, format_instructions=CSVinstructions, invoiceID=invoiceID, format="csv")

@app.route('/invoice/JSON', methods = ['GET', 'POST'])
@login_required
def create_invoice_JSON():
    form = JSONFile()
    invoiceID = None
    try:
        if (form.validate_on_submit()):
            file = form.file.data
            if not os.path.exists('static/'):
                os.makedirs('static/')
            file.save(app.config['JSONFiles'] + file.filename)
            invoiceID = processJSON(app.config['JSONFiles'] + file.filename, current_user.id)
            toXml(invoiceID)
    except UnicodeDecodeError as decode_error:
        os.remove(app.config['JSONFiles'] + file.filename)
        error_message = f"The file {file.filename} is not a valid JSON file."
        return render_template('error.html', error_message=error_message, status=0), 400
    except json.JSONDecodeError as e:
        os.remove(app.config['JSONFiles'] + file.filename)
        error_message = f"The file {file.filename} had a decoding error: {e}"
        return render_template('error.html', error_message=error_message, status=0), 400
    except Exception as error:
        error_message = str(error)
        return render_template('error.html', error_message=error_message, status=0), 400

    return render_template('index.html', form = form, format_instructions=JSONinstructions, invoiceID=invoiceID, format="json")

@app.route('/invoice/GUI', methods = ['GET', 'POST'])
@login_required
def create_GUI():
    invoiceID = None
    if request.method == 'POST':
        try:
            invoiceID = processGUI(request.form, current_user.id)
            toXml(invoiceID)
        except Exception as error:
            error_message = str(error)
            return render_template('error.html', error_message=error_message, status=0), 400            
    return render_template('gui.html', invoiceID=invoiceID)


@app.route('/invoice')
@login_required
def get_ids():
    db = psycopg2.connect(
        dbname="invoicedata",
        user="ubuntu",
        password="ubuntu",
        host="3.27.23.157",
        port="5432"
    )    
    cur = db.cursor()

    try:
        cur.execute("SELECT id FROM invoice WHERE userID = %s ORDER BY ID", [current_user.id])
        invoice_ids = [row[0] for row in cur.fetchall()]
        return render_template('showall.html', invoice_ids=invoice_ids), 200
    except Exception as e:
        error_message = f"Failed to retrieve invoice IDs: {e}"
        return render_template('error.html', error_message=error_message, status=0), 400
    finally:
        db.close()

@app.route('/clear/invoice/<id>', methods=['GET', 'DELETE'])
@login_required
def clear_invoice(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    if request.method == 'DELETE':
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )
        cur = db.cursor()
        try:
            cur.execute("DELETE FROM invoice WHERE id = %s", [id])
            db.commit()
            os.remove('static/XMLFiles/'+str(id)+'.xml')
            if os.path.exists('static/RenderedInvoice/'+str(id)+'.html'):
                os.remove('static/RenderedInvoice/'+str(id)+'.html')
            if os.path.exists('static/RenderedInvoice/'+str(id)+'.json'):
                os.remove('static/RenderedInvoice/'+str(id)+'.json')
            if os.path.exists('static/Validation/report'+str(id)+'.html'):
                os.remove('static/Validation/report'+str(id)+'.html')
        except Exception as e:
            db.rollback()
            error_message =f"Failed to delete invoice {id}: {e}"
            return error_message, 400
        finally:
            if db:
                db.close()
        return f"Invoice {id} deleted successfully", 200
    else:
        return render_template('delete.html', invoice_id=id)

@app.route('/invoice/<id>', methods = ['GET', 'PUT'])
@login_required
def get_invoice(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    if request.method == 'GET':
        toXml(id)
        with open(f"static/XMLFiles/{id}.xml") as file:
            invoice = file.read()

        return render_template('displayxml.html', xml_data = invoice, invoice_id=id)
    elif request.method == 'PUT':
        return redirect(url_for('update_invoice', id=id))

@app.route('/update/invoice/<id>', methods=['GET', 'POST'])
@login_required
def update_invoice(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    if request.method == 'GET':
        try:
            db = psycopg2.connect(
                dbname="invoicedata",
                user="ubuntu",
                password="ubuntu",
                host="3.27.23.157",
                port="5432"
            )            
            cur = db.cursor()

            cur.execute("SELECT * FROM invoice WHERE ID = %s", (id,))
            invoice_info = cur.fetchone()

            cur.execute("SELECT * FROM product WHERE iID = %s ORDER BY pID", (id,))
            product_info = cur.fetchall()

            db.close()

            return render_template('update.html', invoice_info=invoice_info, product_info=product_info, invoice_id=id)
        except psycopg2.Error as e:
            error_message = f"Database error: {e}"
            return render_template('error.html', error_message=error_message, status=0), 400
    elif request.method == 'POST':
        try:
            update(request.json, id)
            toXml(id)
            return jsonify({"message" : f"Invoice {id} updated successfully"}), 200
        except Exception as e:
            # print(e)
            return jsonify({"message" : f"Error has occured: {e}"}), 400

@app.route('/invoice/<id>/html', methods = ['GET'])
@login_required
def get_rendered_html(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    fetch_api_html(int(id))
    data = display_html(int(id))
    return data

@app.route('/invoice/<id>/json', methods = ['GET'])
@login_required
def get_rendered_json(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    fetch_api_json(int(id))
    invoice = display_json(int(id))
    return render_template('displayjson.html', xml_data=invoice, invoice_id=id)

def base63ToHex(hex):
    hex_string = hex[2:]
    bytes_obj = binascii.unhexlify(hex_string)
    return bytes_obj.decode('utf-8') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )        
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE UserName = %s", [form.username.data])
        user = cur.fetchone()
        if user:
            if bcrypt.check_password_hash(base63ToHex(user[2]), form.password.data):
                login_user(User.get(user[0]))
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        db = psycopg2.connect(
            dbname="invoicedata",
            user="ubuntu",
            password="ubuntu",
            host="3.27.23.157",
            port="5432"
        )
        cur = db.cursor()
        cur.execute(addUserQuery,[form.username.data, hashed_password])
        db.commit()
        db.close()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/invoice/<id>/validate', methods = ['GET'])
@login_required
def get_report(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    fetch_report(int(id))
    data = display_report(int(id))
    return data

@app.route('/invoice/<id>/download', methods = ['GET'])
@login_required
def download_invoice(id):
    try:
        accessCheck(current_user.id, id)
    except PermissionError as pe:
        error_message = str(pe)
        return render_template('error.html', error_message=error_message, status=4), 404
    except ExistenceError as ee:
        error_message = str(ee)
        return render_template('error.html', error_message=error_message, status=0), 400

    toXml(id)
    pth = get_invoice_path(int(id))
    return send_file(pth, as_attachment=True)

@app.route('/format/<format>', methods = ['GET'])
@login_required
def download_format(format):
    pth = get_format_path(str(format))
    return send_file(pth, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)