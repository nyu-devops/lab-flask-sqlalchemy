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
Pet API Controller

This modules provides a REST API for the Pet Model

Paths:
------
GET /pets - Lists all of the Pets
GET /pets/{id} - Retrieves a single Pet with the specified id
POST /pets - Creates a new Pet
PUT /pets/{id} - Updates a single Pet with the specified id
DELETE /pets/{id} - Deletes a single Pet with the specified id
POST /pets/{id}/purchase - Action to purchase a Pet
"""

import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from app.models import Pet, Category, DataValidationError
from app import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Send back the home page """
    return app.send_static_file('index.html')

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    """ Returns all of the Pets """
    app.logger.info('Listing Pets...')
    pets = []
    category = request.args.get('category')
    name = request.args.get('name')
    available = request.args.get('available')
    if category:
        pets = Pet.find_by_category(category)
    elif name:
        pets = Pet.find_by_name(name)
    elif available:
        pets = Pet.find_by_availability(available.lower() in ['true', '1', 't'])
    else:
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)

@app.route('/pets/sorted', methods=['GET'])
def list_sorted():
    """ Returns all of the Pets """
    app.logger.info('Get sorted Pets...')
    pets = []
    pets = Pet.all_sorted()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    app.logger.info('Retrieve a Pet with ID:(%s)...', pet_id)
    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pets():
    """
    Creates a Pet

    This endpoint will create a Pet based the data in the body that is posted
    or data that is sent via an html form post.
    """
    app.logger.info('Creating Pet...')
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Processing FORM data')
        data = {
            'name': request.form['name'],
            'category_id': request.form['category'],
            'available': request.form['available'].lower() in ['true', '1', 't']
        }
    else:
        app.logger.info('Processing JSON data')
        data = request.get_json()
    pet = Pet()
    pet.deserialize(data)
    pet.save()
    message = pet.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': url_for('get_pets', pet_id=pet.id, _external=True)})

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    app.logger.info('Updating a Pet with ID:(%s)...', pet_id)
    pet = Pet.find_or_404(pet_id)
    pet.deserialize(request.get_json())
    pet.id = pet_id
    pet.save()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    app.logger.info('Deleting a Pet with ID:(%s)...', pet_id)
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
######################################################################
#  C A T E G O R Y   R O U T E S
######################################################################
######################################################################


######################################################################
# LIST ALL CATEGORIES
######################################################################
@app.route('/categories', methods=['GET'])
def list_categories():
    """ Returns all of the Categories """
    app.logger.info('Listing Categories...')
    categories = Category.all()
    results = [category.serialize() for category in categories]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A CATEGORY
######################################################################
@app.route('/categories/<int:category_id>', methods=['GET'])
def get_categories(category_id):
    """
    Retrieve a single Category

    This endpoint will return a Category based on it's id
    """
    app.logger.info('Retrieve a Category with ID:(%s)...', category_id)
    category = Category.find(category_id)
    if not category:
        abort(status.HTTP_404_NOT_FOUND, "Category with id '{}' was not found.".format(category_id))
    return make_response(jsonify(category.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW CATEGORY
######################################################################
@app.route('/categories', methods=['POST'])
def create_categories():
    """
    Creates a Category

    This endpoint will create a Category based the data in the body that is posted
    or data that is sent via an html form post.
    """
    app.logger.info('Creating Category...')
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Processing FORM data')
        data = {
            'name': request.form['name'],
        }
    else:
        app.logger.info('Processing JSON data')
        data = request.get_json()
    category = Category()
    category.deserialize(data)
    category.save()
    message = category.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': url_for('get_categories', category_id=category.id, _external=True)})

######################################################################
# UPDATE AN EXISTING CATEGORY
######################################################################
@app.route('/categories/<int:category_id>', methods=['PUT'])
def update_categories(category_id):
    """
    Update a Category

    This endpoint will update a Category based the body that is posted
    """
    app.logger.info('Updating a Category with ID:(%s)...', category_id)
    category = Category.find_or_404(category_id)
    category.deserialize(request.get_json())
    category.id = category_id
    category.save()
    return make_response(jsonify(category.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A CATEGORY
######################################################################
@app.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_categories(category_id):
    """
    Delete a Category

    This endpoint will delete a Category based the id specified in the path
    """
    app.logger.info('Delete a Category with ID:(%s)...', category_id)
    category = Category.find(category_id)
    if category:
        category.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    Pet.init_db()
    Category.init_db()

def truncate_db():
    Pet.delete_all()
    Category.delete_all()

#@app.before_first_request
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
