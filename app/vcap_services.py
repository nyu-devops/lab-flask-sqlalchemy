"""
VCAP Services module

This module initializes the database connection String
from VCAP_SERVICES in Bluemix if Found
"""

import os
import json
import logging

def get_database_url():
    """
    Initialized MySQL database connection

    This method will work in the following conditions:
      1) In Bluemix with Redis bound through VCAP_SERVICES
      2) With MySQL running on the local server as with Travis CI
      3) With MySQL --link in a Docker container called 'mysql'
    """
    # Get the credentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        logging.info("Using VCAP_SERVICES...")
        vcap_services = os.environ['VCAP_SERVICES']
        services = json.loads(vcap_services)
        creds = services['cleardb'][0]['credentials']
        #uri = creds["uri"]
        username = creds["username"]
        password = creds["password"]
        hostname = creds["hostname"]
        port = creds["port"]
        name = creds["name"]
    else:
        logging.info("Using defaults...")
        username = 'root'
        password = 'passw0rd'
        hostname = 'localhost'
        port = '3306'
        name = 'development'

    logging.info("Conecting to cleardb on host %s port %s", hostname, port)
    connect_string = 'mysql+pymysql://{}:{}@{}:{}/{}'
    return connect_string.format(username, password, hostname, port, name)
