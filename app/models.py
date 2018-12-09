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

class Category(db.Model):
    """ Category of Pet """
    logger = logging.getLogger(__name__)

    # Table Schema
    #__tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    members = db.relationship("Pet")

    def __repr__(self):
        return '<Category %r>' % (self.name)

    def save(self):
        """ Saves an existing Category in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes a Category from the database """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ serializes a Category into a dictionary """
        return {"id": self.id,
                "name": self.name}

    def deserialize(self, data):
        """ deserializes a Category my marshalling the data """
        try:
            self.name = data['name']
        except KeyError as error:
            raise DataValidationError('Invalid Category: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Category: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls):
        """ Initializes the database session """
        cls.logger.info('Category: Initializing database')
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def delete_all(cls):
        cls.query.delete()
        db.session.commit()

    @classmethod
    def all(cls):
        """ Return all of the Categories in the database """
        cls.logger.info('Processing all Categories')
        return cls.query.all()

    @classmethod
    def find(cls, category_id):
        """ Find a Category by it's id """
        cls.logger.info('Processing category lookup for id %s ...', category_id)
        return cls.query.get(category_id)

    @classmethod
    def find_or_404(cls, category_id):
        """ Find a Category by it's id """
        cls.logger.info('Processing category lookup or 404 for id %s ...', category_id)
        return cls.query.get_or_404(category_id)

    @classmethod
    def find_by_name(cls, name):
        """ Query that finds Categories by their name """
        cls.logger.info('Processing category name query for %s ...', name)
        return cls.query.filter(Category.name == name)



######################################################################
# Pet Model for database
######################################################################
class Pet(db.Model):
    """A single pet"""
    logger = logging.getLogger(__name__)

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
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
                "category_id": self.category_id,
                "available": self.available}

    def deserialize(self, data):
        """ deserializes a Pet my marshalling the data """
        try:
            self.name = data['name']
            self.category_id = data['category_id']
            self.available = data['available']
        except KeyError as error:
            raise DataValidationError('Invalid pet: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid pet: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls):
        """ Initializes the database session """
        cls.logger.info('Pet: Initializing database')
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def delete_all(cls):
        cls.query.delete()
        db.session.commit()

    @classmethod
    def all(cls):
        """ Return all of the Pets in the database """
        cls.logger.info('Processing all Pets')
        return Pet.query.all()

    @classmethod
    def all_sorted(cls):
        """ Return all of the Pets in the database """
        cls.logger.info('Processing all Pets')
        return Pet.query.order_by(Pet.name.desc()).all()

    @classmethod
    def find(cls, pet_id):
        """ Find a Pet by it's id """
        cls.logger.info('Processing lookup for id %s ...', pet_id)
        return Pet.query.get(pet_id)

    @classmethod
    def find_or_404(cls, pet_id):
        """ Find a Pet by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', pet_id)
        return Pet.query.get_or_404(pet_id)

    @classmethod
    def find_by_name(cls, name):
        """ Query that finds Pets by their name """
        cls.logger.info('Processing name query for %s ...', name)
        return Pet.query.filter(Pet.name == name)

    @classmethod
    def find_by_category(cls, category):
        """ Query that finds Pets by their category """
        cls.logger.info('Processing category query for %s ...', category)
        return Pet.query.filter(Pet.category_id == category)

    @classmethod
    def find_by_availability(cls, available=True):
        """ Query that finds Pets by their availability """
        cls.logger.info('Processing available query for %s ...', available)
        return Pet.query.filter(Pet.available == available)
