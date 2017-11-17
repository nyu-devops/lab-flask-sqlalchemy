"""
Microservice module

This module contains the microservice code for
    server
    models
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.vcap_services import get_database_url

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.logger.info(app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)

from app import server, models
