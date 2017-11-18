#!usr//bin/python
"""
Database Creation Script

This Python script will create the database base on the
environment variables DATABASE_URI or SQLALCHEMY_DATABASE_URI
in that order. (DATABASE_URI overrides SQLALCHEMY_DATABASE_URI)
You can also override the database name in the URI by passing
in a new name.

Enviroment Variables:
---------------------
    - SQLALCHEMY_DATABASE_URI : connection string from config
    - DATABASE_URI: override config string

Arguments:
----------
    - database_name : String the name of the database
"""
import os
import sys
import pymysql
from app import app, db

# DATABASE_URI = 'mysql+pymysql://root:passw0rd@localhost:3306/development'
DATABASE_URI = os.getenv('DATABASE_URI', None)
if DATABASE_URI:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

# check to see if there is a database name override
if len(sys.argv) > 1:
    dbname = sys.argv[1]
    app.config['SQLALCHEMY_DATABASE_URI'] = '{}/{}'.format(
        app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[0],
        dbname
    )

print('Database URI {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

try:
    print "Creating database tables"
    db.create_all()
except Exception as error:
    print 'Oops, got error {}'.format(error.message)

    # Parse the URI for user, password, host
    data = app.config['SQLALCHEMY_DATABASE_URI'].split('//')[1]
    dbname = data.split('/')[1]
    host = data.split('@')[1].split(':')[0]
    creds = data.split('@')[0]
    user = creds.split(':')[0]
    password = creds.split(':')[1]

    # Connect and create the database
    conn = pymysql.connect(host=host, user=user, password=password)
    conn.cursor().execute('create database IF NOT EXISTS {}'.format(dbname))
    print "Creating database tables"
    db.create_all()
