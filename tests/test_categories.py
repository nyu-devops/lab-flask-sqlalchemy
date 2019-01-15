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
Category Model Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
coverage report -m
"""

import os
import unittest
from app import app, db
from app.models import Category, DataValidationError

# DATABASE_URI = 'mysql+pymysql://root:passw0rd@localhost:3306/test'
DATABASE_URI = os.getenv('DATABASE_URI', None)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestCategory(unittest.TestCase):
    """ Test Cases for Categories """

    @classmethod
    def setUpClass(cls):
        app.debug = False
        # Set up the test database
        if DATABASE_URI:
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        db.drop_all()       # clean up the last tests
        db.create_all()     # make our sqlalchemy tables

    @classmethod
    def tearDownClass(cls):
        #db.drop_all()       # clean up after the last test
        db.session.remove() # disconnect from database

    def setUp(self):
        Category.delete_all()   # truncate catrgory table

    def tearDown(self):
        pass

    def test_create_a_category(self):
        """ Create a category and assert that it exists """
        category = Category(name="Cat")
        self.assertTrue(category != None)
        self.assertEqual(category.id, None)
        self.assertEqual(category.name, "Cat")

    def test_add_a_category(self):
        """ Create a category and add it to the database """
        categories = Category.all()
        self.assertEqual(categories, [])
        category = Category(name="Dog")
        self.assertTrue(category != None)
        self.assertEqual(category.id, None)
        category.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(category.id, None)
        categories = Category.all()
        self.assertEqual(len(categories), 1)

    def test_update_a_category(self):
        """ Update a Category """
        category = Category(name="Dog")
        category.save()
        self.assertNotEqual(category.id, None)
        category_id = category.id
        # Change it an save it
        category.name = "K9"
        category.save()
        self.assertEqual(category.id, category_id)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        categories = Category.all()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "K9")

    def test_delete_a_category(self):
        """ Delete a Category """
        category = Category(name="Dog")
        category.save()
        self.assertEqual(len(Category.all()), 1)
        # delete the category and make sure it isn't in the database
        category.delete()
        self.assertEqual(len(Category.all()), 0)

    def test_serialize_a_category(self):
        """ Test serialization of a Category """
        category = Category(name="Dog")
        data = category.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "Dog")

    def test_deserialize_a_category(self):
        """ Test deserialization of a Category """
        data = {"id": 1, "name": "Cat"}
        category = Category()
        category.deserialize(data)
        self.assertNotEqual(category, None)
        self.assertEqual(category.id, None)
        self.assertEqual(category.name, "Cat")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Category without a name """
        category = Category()
        data = {"id":0}
        self.assertRaises(DataValidationError, category.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Category with no data """
        category = Category()
        self.assertRaises(DataValidationError, category.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Category with bad data """
        category = Category()
        self.assertRaises(DataValidationError, category.deserialize, "data")

    def test_find_category(self):
        """ Find a Category by ID """
        Category(name="Dog").save()
        cat = Category(name="Cat")
        cat.save()
        category = Category.find(cat.id)
        self.assertIsNot(category, None)
        self.assertEqual(category.id, cat.id)
        self.assertEqual(category.name, "Cat")

    def test_find_with_no_categories(self):
        """ Find a Category with no Categorys """
        category = Category.find(1)
        self.assertIs(category, None)


    def test_category_not_found(self):
        """ Test for a Category that doesn't exist """
        Category(name="Dog").save()
        category = Category.find(99999)
        self.assertIs(category, None)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestCategorys)
    # unittest.TextTestRunner(verbosity=2).run(suite)
