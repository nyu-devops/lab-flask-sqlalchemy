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
VCAP Services module

This module initializes the database connection String
from VCAP_SERVICES in Bluemix if Found
"""
import os
import json
from flask import current_app

def get_database_uri():
    """
    Initialized DB2 database connection

    This method will work in the following conditions:
      1) With DATABASE_URI as an environment variable
      2) In Bluemix with DB2 bound through VCAP_SERVICES
      3) With PostgreSQL running on the local server as with Travis CI
    """
    database_uri = None
    if 'DATABASE_URI' in os.environ:
        # Get the credentials from DATABASE_URI
        current_app.logger.info("Using DATABASE_URI...")
        database_uri = os.environ['DATABASE_URI']
    elif 'VCAP_SERVICES' in os.environ:
        # Get the credentials from the Bluemix environment
        current_app.logger.info("Using VCAP_SERVICES...")
        vcap_services = os.environ['VCAP_SERVICES']
        services = json.loads(vcap_services)
        creds = services['dashDB For Transactions'][0]['credentials']
        database_uri = creds["uri"]
    else:
        current_app.logger.info("Using localhost database...")
        database_uri = "postgres://postgres:postgres@localhost:5432/postgres"

    return database_uri
