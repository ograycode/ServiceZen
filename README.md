# ServiceZen

Manage your SOA automatically.

## About

Servicezen allows you to easily manage and monitor the discovery of your services for your SOA Application. It is based upon standard HTTP protocols, and gives you a simple user interface to add, delete, and monitor groups of services. 

## Usage

Once installed and configured, the only command you need to worry about is setting up some sort of scheduled task to execute the command ``python manage.py pingservices``, which will check the status of all services that have refresh enabled. You can force a check of every service by using ``python manage.py pingservices forceping``.

A service that is up should always return with an http status code of ``200 OK``.

## API

In general, by adding ``?format=json`` to each url, a json formatted view will be returned, but most endpoints require that the the caller be authenticated.

### Authentication

Users can be created through the adminstration panel at ``/admin`` and the API uses a token based authentication scheme. The following is an example of creating a new service using the token based authentication.

    curl -X POST -d "username=user_name&password=secret_password" http://localhost:8000/token/new.json

    {"token": "3m9-273d1cdc7d5863d509b3", "user": 2, "success": true}

    curl -X POST -d "{\"fields\": {\"name\":\"group_one\"}, \"user\":2, \"token\":\"3m9-273d1cdc7d5863d509b3\"}" http://localhost:8000/group/add.json

    [{"pk": 4, "model": "services.servicegroupmodel", "fields": {"name": "group_one"}}]

    curl -X POST -d "{\"fields\": {\"name\":\"service_one\", \"service_group\": 4}, \"user\":2, \"token\":\"3m9-273d1cdc7d5863d509b3\"}" http://localhost:8000/service/add.json

    [{"pk": 2, "model": "services.servicemodel", "fields": {"service_group": 4, "name": "service_one", "url": null, "health_url": null, "created_on": "2013-11-03T23:18:33.347Z", "is_up": false, "is_refresh_on": false}}]

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

## Setup
Ensure that Pip, Django 1.5 and Python 2.7 are installed before proceeding. The following is targeted at Ubuntu based distributions, but should run work on a variety of platforms.

1. ``pip install django-bootstrap3``
2. ``pip install django-tokenapi``
3. ``git clone https://github.com/ograycode/ServiceZen.git``
4. ``cd ServiceZen``
5. ``python manage.py syncdb``
6. ``python manage.py runserver``

### Demo
If you have [Docker](http://www.docker.io) installed, there is already a repo which can be used as a demo.

1. ``sudo docker pull ograycode/service-zen``
1. ``sudo docker run -d -p 8000 ograycode/service-zen python /ServiceZen/manage.py runserver 0.0.0.0:8000``
2. ``sudo docker ps`` to find the port that docker connected to.

The default admin user/password is servicezen_admin/admin_servicezen

## Easy to Extend

Written using Django 1.5 and Python 2.7, it is very easy to extend. In fact there are only three models that make up the core functionality of the application. 

By default, the application uses SQLite, but the database can be switched out by changing a configuration file.

## TODO

Increase test coverage and documentation