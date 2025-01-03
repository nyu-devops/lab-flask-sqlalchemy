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
Pet API Service Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
flake8 server.py --count --max-line-length=127 --statistics --exit-zero
"""

import os
import unittest
import logging
from flask_api import status    # HTTP Status Codes
from app.models import Pet, Category
from app import server, db

#DATABASE_URI = 'mysql+pymysql://root:passw0rd@localhost:3306/test'
DATABASE_URI = os.getenv('DATABASE_URI', "postgresql://postgres:postgres@localhost:5432/postgres")

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(unittest.TestCase):
    """ Pet Server Test Cases """

    @classmethod
    def setUpClass(cls):
        server.app.debug = False
        server.initialize_logging(logging.INFO)
        # Set up the test database
        if DATABASE_URI:
            server.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        db.drop_all()         # clean before all tests
        server.init_db()
        # db.create_all()     # make our sqlalchemy tables

    @classmethod
    def tearDownClass(cls):
        db.drop_all()       # clean up after the last test
        db.session.remove() # disconnect from database

    def setUp(self):
        # Create some categories for the tests
        server.truncate_db()
        # Create some categories for testing
        dog = Category(name="Dog")
        dog.save()
        self.dog_id = dog.id
        cat = Category(name="Cat")
        cat.save()
        self.cat_id = cat.id
        Pet(name='fido', category_id=self.dog_id, available=True).save()
        Pet(name='kitty', category_id=self.cat_id, available=True).save()
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        """ Get the home page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('Pet Demo REST API Service' in resp.data)

    def test_get_pet_list(self):
        """ Get a list of Pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_pet(self):
        """ Get a single Pet """
        # get the id of a pet
        pet = Pet.find_by_name('fido')[0]
        resp = self.app.get('/pets/{}'.format(pet.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], pet.name)

    def test_get_pet_not_found(self):
        """ Get a Pet that doesn't exist """
        resp = self.app.get('/pets/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_pet(self):
        """ Create a new Pet """
        # save the current number of pets for later comparison
        pet_count = self.get_pet_count()
        # add a new pet
        snake = Category(name="Snake")
        snake.save()
        new_pet = {'name': 'sammy', 'category_id': snake.id, 'available': True}
        resp = self.app.post('/pets', json=new_pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'sammy')
        # check that count has gone up and includes sammy
        resp = self.app.get('/pets')
        # print 'resp_data(2): ' + resp.data
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), pet_count + 1)
        self.assertIn(new_json, data)

    def test_update_pet(self):
        """ Update an existing Pet """
        resp = self.app.get('/pets', query_string='name=kitty')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        kitty = data[0]
        self.assertEqual(kitty['name'], 'kitty')
        self.assertEqual(kitty['category_id'], self.cat_id)
        kitty['category_id'] = self.dog_id
        resp = self.app.put('/pets/{}'.format(kitty['id']), json=kitty, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'kitty')
        self.assertEqual(new_json['category_id'], self.dog_id)

    def test_update_pet_with_no_data(self):
        """ Update a Pet with no data passed """
        pet = Pet.find_by_name('kitty')[0]
        resp = self.app.put('/pets/{}'.format(pet.id), data=None, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_with_text_data(self):
        """ Update a Pet with text data """
        pet = Pet.find_by_name('kitty')[0]
        resp = self.app.put('/pets/{}'.format(pet.id), data="hello", content_type='text/plain')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_with_no_name(self):
        """ Update a Pet without a name """
        pet = Pet.find_by_name('kitty')[0]
        new_pet = {'category_id': self.dog_id}
        resp = self.app.put('/pets/{}'.format(pet.id), json=new_pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """ Update a Pet that doesn't exist """
        new_kitty = {'name': 'timothy', 'category_id': self.cat_id, 'available': True}
        resp = self.app.put('/pets/0', json=new_kitty, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_pet(self):
        """ Delete a Pet """
        pet = Pet.find_by_name('fido')[0]
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        resp = self.app.delete('/pets/{}'.format(pet.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_pet_count()
        self.assertEqual(new_count, pet_count - 1)

    def test_create_pet_with_no_data(self):
        """ Try and create Pet with no data """
        resp = self.app.post('/pets', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_with_no_name(self):
        """ Try and create Pet with no name """
        new_pet = {'category_id': self.dog_id, 'available': True}
        resp = self.app.post('/pets', json=new_pet, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """ Create Pet without a Context-Type """
        new_pet = '{"available": true, "category_id": ' + str(self.dog_id) + ', "name": "fifi"}'
        resp = self.app.post('/pets', data=new_pet)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_pet_category(self):
        """ Query Pet by category """
        resp = self.app.get('/pets', query_string='category={}'.format(self.dog_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['category_id'], self.dog_id)

    def test_query_pet_name(self):
        """ Query Pet by name """
        resp = self.app.get('/pets', query_string='name=fido')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = resp.get_json()
        query_item = data[0]
        self.assertEqual(query_item['name'], 'fido')

    def test_query_pet_avail(self):
        """ Query Pet by availability """
        # there should be none that are not available
        # resp = self.app.get('/pets', query_string='available=false')
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(resp.data), 0)
        # there should be available
        resp = self.app.get('/pets', query_string='available=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        # check we have both
        self.assertIn('fido', resp.data)
        self.assertIn('kitty', resp.data)

    def test_method_not_allowed(self):
        """ Test for method now allowed """
        resp = self.app.put('/pets')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#  T E S T   C A T E G O R I E S
######################################################################


    def test_get_category_list(self):
        """ Get a list of Categories """
        resp = self.app.get('/categories')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_category(self):
        """ Get a single Category """
        # get the id of a pet
        category = Category.find_by_name('Dog')[0]
        resp = self.app.get('/categories/{}'.format(category.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], category.name)

    def test_get_category_not_found(self):
        """ Get a Category that doesn't exist """
        resp = self.app.get('/categories/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category(self):
        """ Create a new Category """
        new_category = dict(name='Snake')
        resp = self.app.post('/categories', json=new_category, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'Snake')

    def test_create_category_with_no_data(self):
        """ Try and create Category with no data """
        resp = self.app.post('/categories', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_with_no_name(self):
        """ Try and create Category with no name """
        new_category = {}
        resp = self.app.post('/categories', json=new_category, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_category_no_content_type(self):
        """ Create Category without a Context-Type """
        new_category = dict(name='Snake')
        resp = self.app.post('/categories', data=str(new_category))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category(self):
        """ Update an existing Category """
        category = Category.find_by_name('Dog')[0]
        resp = self.app.get('/categories/{}'.format(category.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], category.name)
        # Change the name to Canine
        data['name'] = 'Canine'
        resp = self.app.put('/categories/{}'.format(data['id']), json=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'Canine')

    def test_update_category_with_no_data(self):
        """ Update a Category with no data passed """
        category = Category.find_by_name('Dog')[0]
        resp = self.app.put('/categories/{}'.format(category.id), json={}, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category_with_text_data(self):
        """ Update a Category with text data """
        category = Category.find_by_name('Dog')[0]
        resp = self.app.put('/categories/{}'.format(category.id), data="hello", content_type='text/plain')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category_not_found(self):
        """ Update a Category that doesn't exist """
        updated_category = dict(name='Foo')
        resp = self.app.put('/categories/0', json=updated_category, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_category(self):
        """ Delete a Category """
        # Create a category with no pets
        category = dict(name='Snake')
        resp = self.app.post('/categories', json=category, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        # Delete the new category
        resp = self.app.delete('/categories/{}'.format(data['id']),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)


######################################################################
# U T I L I T Y   F I X T U R E S
######################################################################
    def truncate_tables(self, session):
        """ Truncates all of the tables """
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            session.execute(table.delete())
        session.commit()

    def get_pet_count(self):
        """ save the current number of pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
