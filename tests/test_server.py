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

import unittest
import logging
import json
from flask_api import status    # HTTP Status Codes
import server

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
        server.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        server.db.drop_all()    # clean up the last tests
        server.Pet.initialize_db(server.db)
        server.Pet(name='fido', category='dog', available=True).save()
        server.Pet(name='kitty', category='cat', available=True).save()
        self.app = server.app.test_client()

    def tearDown(self):
        server.db.session.remove()
        server.db.drop_all()

    def test_index(self):
        """ Get the home page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('Pet Demo REST API Service' in resp.data)

    def test_get_pet_list(self):
        """ get a ist of Pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_pet(self):
        """ Get a single Pet """
        resp = self.app.get('/pets/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'kitty')

    def test_get_pet_not_found(self):
        """ get a Pet that doesn't exist """
        resp = self.app.get('/pets/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_pet(self):
        """ Create a new Pet """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # add a new pet
        new_pet = {'name': 'sammy', 'category': 'snake', 'available': 'True'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'sammy')
        # check that count has gone up and includes sammy
        resp = self.app.get('/pets')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), pet_count + 1)
        self.assertIn(new_json, data)

    def test_update_pet(self):
        """ Update an existing Pet """
        new_kitty = {'name': 'kitty', 'category': 'tabby', 'available': 'True'}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['category'], 'tabby')

    def test_update_pet_with_no_data(self):
        """ Update a Pet with no data passed """
        resp = self.app.put('/pets/2', data=None, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_with_text_data(self):
        """ Update a Pet with text data """
        resp = self.app.put('/pets/2', data="hello", content_type='text/plain')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_with_no_name(self):
        """ Update a Pet without a name """
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """ Update a Pet that doesn't exist """
        new_kitty = {'name': 'timothy', 'category': 'mouse', 'available': 'True'}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_pet(self):
        """ Delete a Pet """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # delete a pet
        resp = self.app.delete('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_pet_count()
        self.assertEqual(new_count, pet_count - 1)

    def test_create_pet_with_no_data(self):
        """ Try and create with no data """
        resp = self.app.post('/pets', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_with_no_name(self):
        """ Try and create with no name """
        new_pet = {'category': 'dog', 'available': 'True'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """ Create without a Context-Type """
        new_pet = {'name': 'fifi', 'category': 'dog', 'available': 'True'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_pet_category(self):
        """ Query Pet by category """
        resp = self.app.get('/pets', query_string='category=dog')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'dog')

    def test_query_pet_name(self):
        """ Query Pet by name """
        resp = self.app.get('/pets', query_string='name=fido')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = json.loads(resp.data)
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
# Utility functions
######################################################################

    def get_pet_count(self):
        """ save the current number of pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
