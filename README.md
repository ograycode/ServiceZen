# ServiceZen

Manage your SOA automatically.

## About

Servicezen allows you to easily manage and monitor the discovery of your services for your SOA Application. It is based upon standard HTTP protocols, and gives you a simple user interface to add, delete, and monitor groups of services. 

## Usage

Once installed and configured, the only command you need to worry about is setting up some sort of scheduled task to execute the command ``python manage.py pingservices``, which will check the status of all services that have refresh enabled. You can force a check of every service by using ``python manage.py pingservices forceping``.

A service that is up should always return with an http status code of ``200 OK``.

## API
In general, by adding ``?format=json`` to each url, a json formatted view will be returned.

### Services

**GET**

*   ``/?format=json`` returns a list of all services
*   ``/service/[primary_key]/?format=json`` returns a detailed view of the given service
*   ``/service/[primary_key]/ping`` forces a ping of a given service

**POST/PUT**

*   ``/service/add.json`` will create a new service
*   ``/service/[primary_key]/edit.json`` will edit an existing service

**DELETE**

*   ``/service/[primary_key]/delete`` will delete an existing service

### Service Groups

**GET**

*   ``/group/[primary_key]/?format=json`` returns a detailed view of the service group

**POST/PUT**

*   ``/group/add.json`` creates a service group
*   ``/group/[primary_key]/edit.json`` edits an existing service group

**DELETE**

*   ``/group/[primary_key]/delete`` deletes an existing service group, and all services associated to it

## Dependencies

*   django-bootstrap3
*   django-tokenapi

## Easy to Extend

Written using Django 1.5 and Python 2.7, it is very easy to extend. In fact there are only three models that make up the core functionality of the application. 

By default, the application uses SQLite, but the database can be switched out by changing a configuration file.

## TODO

Increase test coverage and documentation