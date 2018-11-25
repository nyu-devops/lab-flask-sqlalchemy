#!usr//bin/python
"""
Database Schema Creation Script

This Python script will create the database schema base on the
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
#import pymysql
import psycopg2
from app import app, db

# DATABASE_URI = 'mysql+pymysql://root:passw0rd@localhost:3306/development'
DATABASE_URI = os.getenv('DATABASE_URI', None)

if __name__ == '__main__':
    if DATABASE_URI:
        print('Using: {}'.format(DATABASE_URI))
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    else:
        print('DATABASE_URI not set, using SQLALCHEMY_DATABASE_URI from app.')

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
        print('Creating database schema...')
        db.create_all()
        print('Schema created.')
    except Exception as error:
        print('Oops, got error {}'.format(error.message))
