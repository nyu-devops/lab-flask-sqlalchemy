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
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    session = None  # database session
    logger = logging.getLogger(__name__)

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    category = db.Column(db.String(63))
    available = db.Column(db.Boolean())

    def save(self):
        """ Saves an existing Pet in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            Pet.session.add(self)
        Pet.session.commit()

    def delete(self):
        """ Deletes a Pet from the database """
        Pet.session.delete(self)
        Pet.session.commit()

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
    def init_db(app):
        """ Initializes the database session """
        Pet.logger.info('Initializing with app %s ...', app)
        db.init_app(app)
        app.app_context().push()
        Pet.session = db.session
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


# VCAP_SERVICES = {
#     "cleardb": [
#         {
#             "credentials":
#             {
#                 "jdbcUrl": "jdbc:mysql://us-cdbr-sl-dfw-01.cleardb.net/ibmx_ed7eeb7522f40eb?user=b233c70a6246c9&password=fadfaef3",
#                 "uri": "mysql://b233c70a6246c9:fadfaef3@us-cdbr-sl-dfw-01.cleardb.net:3306/ibmx_ed7eeb7522f40eb?reconnect=true",
#                 "name": "ibmx_ed7eeb7522f40eb",
#                 "hostname": "us-cdbr-sl-dfw-01.cleardb.net",
#                 "port": "3306",
#                 "username": "b233c70a6246c9",
#                 "password": "fadfaef3"
#             }
#         }
#     ]
# }

    # @staticmethod
    # def init_db():
    #     """
    #     Initialized MySQL database connection
    #
    #     This method will work in the following conditions:
    #       1) In Bluemix with Redis bound through VCAP_SERVICES
    #       2) With MySQL running on the local server as with Travis CI
    #       3) With MySQL --link in a Docker container called 'mysql'
    #
    #     Exception:
    #     ----------
    #       DatabaseConnectionError - if connection fails
    #     """
    #     # Get the credentials from the Bluemix environment
    #     if 'VCAP_SERVICES' in os.environ:
    #         Pet.logger.info("Using VCAP_SERVICES...")
    #         vcap_services = os.environ['VCAP_SERVICES']
    #         services = json.loads(vcap_services)
    #         creds = services['cleardb'][0]['credentials']
    #         Pet.logger.info("Conecting to cleardb on host %s port %s",
    #                         creds['hostname'], creds['port'])
    #         jdbcUrl =    "jdbcUrl": "jdbc:mysql://us-cdbr-sl-dfw-01.cleardb.net/ibmx_ed7eeb7522f40eb?user=b233c70a6246c9&password=fadfaef3",
    #         uri =     "uri": "mysql://b233c70a6246c9:fadfaef3@us-cdbr-sl-dfw-01.cleardb.net:3306/ibmx_ed7eeb7522f40eb?reconnect=true",
    #         name =    "name": "ibmx_ed7eeb7522f40eb",
    #         hostname =    "hostname": "us-cdbr-sl-dfw-01.cleardb.net",
    #         port =    "port": "3306",
    #         username=     "username": "b233c70a6246c9",
    #             "password": "fadfaef3"
    #
    #
    #         Pet.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    #     else:
    #         Pet.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
    #         Pet.connect_to_redis('127.0.0.1', 6379, None)
    #         if not Pet.redis:
    #             Pet.logger.info("No Redis on localhost, looking for redis host")
    #             Pet.connect_to_redis('redis', 6379, None)
    #     if not Pet.redis:
    #         # if you end up here, redis instance is down.
    #         Pet.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
    #         raise DatabaseConnectionError('Could not connect to the Redis Service')
