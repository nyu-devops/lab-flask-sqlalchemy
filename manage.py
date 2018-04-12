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
import re
import pymysql
from app import app, db

# DATABASE_URI = 'mysql+pymysql://root:passw0rd@localhost:3306/development'
DATABASE_URI = os.getenv('DATABASE_URI', None)

if __name__ == '__main__':
    if DATABASE_URI:
        print 'Using: {}'.format(DATABASE_URI)
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    else:
        print 'DATABASE_URI not set, using SQLALCHEMY_DATABASE_URI from app.'

    # check to see if there is a database name override
    if len(sys.argv) > 1:
        dbname = sys.argv[1]
        app.config['SQLALCHEMY_DATABASE_URI'] = '{}/{}'.format(
            app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[0],
            dbname
        )

    print('Database URI {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

    # If the database doesn't exist an exception will be thrown
    # so we catch it and create the database
    try:
        print "Creating database tables"
        db.create_all()
    except Exception as error:
        print 'Oops, got error {}'.format(error.message)

        # Parses a database url into it's credentials
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print 'Attempting to parse: {}'.format(database_uri)
        uri_regex = r'^(.*:)\/\/(.*):(.*)@([A-Za-z0-9\-\.]+):([0-9]+)\/(.*)$'
        tokens = re.search(uri_regex, database_uri)
        prefix = tokens.group(1)
        user = tokens.group(2)
        password = tokens.group(3)
        host = tokens.group(4)
        port = int(tokens.group(5))
        dbname = tokens.group(6)

        # Connect and create the database
        conn = pymysql.connect(host=host, user=user, password=password)
        conn.cursor().execute('create database IF NOT EXISTS {}'.format(dbname))
        print "Creating database tables"
        db.create_all()
