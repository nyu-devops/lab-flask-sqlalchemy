# lab-flask-sqlalchemy

<!-- [![Build Status](https://travis-ci.org/rofrano/lab-flask-tdd.svg?branch=master)](https://travis-ci.org/rofrano/lab-flask-tdd)
[![Codecov](https://img.shields.io/codecov/c/github/rofrano/lab-flask-tdd.svg)]() -->

NYU DevOps lab on using SQLAlchemy with Flask

## Introduction

This lab shows how to use SQLAlchemy with Flask so that you don't need to worry about making raw database queries. SQLAlchemy is an Object Relational Mapper (ORM) that will allow you to work with classes instead of database records. This example extends our Pet Store to use a relational database for it's persistence.

This lab also demonstrates how to create a simple RESTful service using Python Flask and SQLite or MySQL.
The resource model is persistences using SQLAlchemy to keep the application simple. It's purpose is to show the correct API and return codes that should be used for a REST API.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with **Vagrant** and **VirtualBox**. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Then all you have to do is clone this repo and invoke vagrant:

    git clone https://github.com/nyu-devops/lab-flask-sqlalchemy.git
    cd lab-flask-sqlalchemy
    vagrant up
    vagrant ssh
    cd /vagrant

The `Vagrantfile` uses Docker to bring up a container running **MariaDB** so that you can test with an actual MySQL database indie of the virtual machine.

## Prerequisite Installation using Docker

If you want to use **Docker** instead of Vagrant and VirtualBox you will need to have Docker installed first. Use either Docker for Mac or Docker for Windows depending on your computer. Then the command to initialize the database is:

```
    docker-compose run --rm web flask db upgrade
```

To run the application use:

```
    docker-compose up -d
```

You can skip the next section on creating the database. Docker-compose just did that for you.

## Manually running the Tests

Run the tests using `nose`

    $ nosetests

**Nose** is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red. It also has `--with-coverage` specified so that code coverage is included in the tests.

The Code Coverage tool runs with `nosetests` so to see how well your test cases exercise your code just run the report:

    $ coverage report -m

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases.

To run the service use (Press Ctrl+C to exit):

    $ python run.py

When you are done, you can exit and shut down the vm with:

    $ exit
    $ vagrant halt

If the VM is no longer needed you can remove it with:

    $ vagrant destroy


## What's featured in the project?

    * manage.py -- used to create the database and schema
    * app/server.py -- the main Service using Python Flask
    * app/models.py -- the database models
    * app/vcap_services.py -- Cloud Foundry VCAP_SERVICES support
    * tests/test_server.py -- test cases using unittest
    * tests/test_pets.py -- test cases using just Pets from the Pet model
    * tests/test_categories.py -- test cases using just Category from the Pet model

This repo is part of the DevOps course CSCI-GA.2820-001/002 at NYU taught by John Rofrano.
