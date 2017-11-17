# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pet Model

This model uses SQLAlchemy to persist itself
"""
import os
import json
import logging
from . import db

######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# Pet Model for database
######################################################################
class Pet(db.Model):
    """A single pet"""
    logger = logging.getLogger(__name__)

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
    available = db.Column(db.Boolean())

    def __repr__(self):
        return '<Pet %r>' % (self.name)

    def save(self):
        """ Saves an existing Pet in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes a Pet from the database """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ serializes a Pet into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "category": self.category,
                "available": self.available}

    def deserialize(self, data):
        """ deserializes a Pet my marshalling the data """
        try:
            self.name = data['name']
            self.category = data['category']
            self.available = data['available']
        except KeyError as error:
            raise DataValidationError('Invalid pet: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid pet: body of request contained' \
                                      'bad or no data')
        return self

    @staticmethod
    def init_db():
        """ Initializes the database session """
        Pet.logger.info('Initializing database')
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def all():
        """ Return all of the Pets in the database """
        Pet.logger.info('Processing all Pets')
        return Pet.query.all()

    @staticmethod
    def find(pet_id):
        """ Find a Pet by it's id """
        Pet.logger.info('Processing lookup for id %s ...', pet_id)
        return Pet.query.get(pet_id)

    @staticmethod
    def find_or_404(pet_id):
        """ Find a Pet by it's id """
        Pet.logger.info('Processing lookup or 404 for id %s ...', pet_id)
        return Pet.query.get_or_404(pet_id)

    @staticmethod
    def find_by_name(name):
        """ Query that finds Pets by their name """
        Pet.logger.info('Processing name query for %s ...', name)
        return Pet.query.filter(Pet.name == name)

    @staticmethod
    def find_by_category(category):
        """ Query that finds Pets by their category """
        Pet.logger.info('Processing category query for %s ...', category)
        return Pet.query.filter(Pet.category == category)

    @staticmethod
    def find_by_availability(available=True):
        """ Query that finds Pets by their availability """
        Pet.logger.info('Processing available query for %s ...', available)
        return Pet.query.filter(Pet.available == available)
