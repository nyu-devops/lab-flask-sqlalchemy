# lab-flask-sqlalchemy

This repo demonstrates how to create a simple RESTful service using Python Flask and MySQL.
The resource model is persistences using SQLAlchemy to keep the application simple. It's purpose is to show the correct API and return codes that should be used for a REST API.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download [VirtualBox](https://www.virtualbox.org/)

Download [Vagrant](https://www.vagrantup.com/)

Clone the project to your development folder and create your Vagrant vm

    $ git clone https://github.com/nyu-devops/lab-flask-sqlalchemy.git
    $ cd lab-flask-sqlalchemy
    $ vagrant up

Once the VM is up you can use it with:

    $ vagrant ssh
    $ cd /vagrant
    $ python server.py

You can run the unit tests with:

    $ nosetests -v --rednose

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

    $ exit
    $ vagrant halt

If the VM is no longer needed you can remove it with:

    $ vagrant destroy
