#!usr//bin/python
"""
Simple script to create the database tables from the models
"""
import os
from app import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == '__main__':
    try:
        print('Creating database schema...')
        db.create_all()
        print('Schema created.')
    except Exception as error:
        print('Oops, got error {}'.format(error.message))
