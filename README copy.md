# While inside of virtual environment 
pip install Flask
pip install Flask_wtf
export FLASK_APP=server.py
flask run

# While inside of postgres
dropdb invoicedata
createdb invoicedata
psql invoicedata -f invoice.sql
psql invoicedata
\i grant_privileges.sql