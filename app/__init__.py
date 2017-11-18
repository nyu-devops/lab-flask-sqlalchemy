"""
Microservice module

This module contains the microservice code for
    server
    models
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
#print('Database URI {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))

db = SQLAlchemy(app)

from app import server, models
