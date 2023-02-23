# Readme
This project uses the Django Rest Framework to implement a RESTful API for a restaurant allowing the staff to manage their tables, reservations with each member of the staff having their respective permissions and roles.

## Required Packages:
This projects is written in python and uses the following packages
- django
- django rest framework
 - psycopg2
 

```
pip install Django
pip install djangorestframework
pip install markdown       
pip install django-filter  
pip install psycopg2
```

## Create the database:
Use the pgAdmin interface or use the following SQL to create the database. A SQL file is included as well
```
CREATE DATABASE restaurant_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
```

 ## Create Migrations:
 Use the following commands to create migrations for the database
 - python manage.py makemigrations
 - python manage.py migrate

 ## Create Admin User:
 To get an admin account which is required to create Employee accounts and Admin account use the following command with role being "Admin" (without the quotes).
 - python manage.py createsuperuser

## Login and get token:
use the /api/users/login endpoint with the following format for the POST request
```
{
  "user": {
    
    "emp_number": "",
    "password": ""
	}
}
```
to get the authorization token with the authorization header being
```
Authorization: Token + ACCOUNT_TOKEN_HERE
```

## Postman Collections and Environment
The postman collection and environment are included.
Set The AUTH_TOKEN_HEADER environment variable to your specified user token.
## Algorithm diagrams and flowcharts
The diagrams are included in the Diagrams folder

 
## Running Tests:
use the following to run the automated tests

 - python manage.py test
 
 ## Running local dev server:
 use the following to run the local server
 tests in ./TableMangement/tests.py

 - python manage.py runserver

## Endpoints:

 - /api/users/register **POST**
 -- admin account required for access
 -- example request: 
 ``` 
 {
  "user": {
    "emp_name": "test3",
    "emp_number": "1386",
    "role": "Employee",
    "password": "testtest"
}
}
```

 - /api/users/login **POST**
-- example request:
```
{
  "user": {
    
    "emp_number": "3333",
    "password": "passowrd"
	}
}
```

 - /api/table/addtable **POST**
--  admin account required for access
-- example request:
 ```
 {
  "table": {
    "table_number" : 3,
    "num_seats": 2
  }
}
 ```
 
 - /api/table/gettables **GET**
-- admin account required for access

 - /api/table/deletetable/int:table_number **DELETE**
-- admin account required for access

 - /api/reservation/setreservation **POST**
-- example request:
```
{
  "reservation": {
    "table_number": 3,
    "start_time":"2023-02-22 23:45:06",
    "end_time": "2023-02-22 23:55:06"
  }
  
}
```
 - /api/reservation/getallreservations **GET**
-- admin account required for access

 - /api/reservation/getallreservations **POST**
-- admin account required for access
-- used to filter by table number
---- example request:
```
{
  "tables":[1,2]
}
```
 - /reservation/deletereservation/int:id **DELETE**
 
 - /api/reservation/getallreservationstoday **GET**
 
 - /api/reservation/gettimeslots/int:required_seats **GET**
 - /api/reservation/getallreservationsfromdate/date:start/date:end **GET**
-- admin account required for access
 - /api/reservation/getallreservationsfromdate/date:start/date:end **POST**
-- admin account required for access
-- used to filter by table number
---- example request:
```
{
  "tables":[1,2]
}
```
 - /api/reservation/getallreservationstoday/str:'asc' *or* str:'desc' **GET**

# Models
## User
| Field | Type | Description |
|--|--|--|
| emp_name | CharField | The employee name
| emp_number  |CharField  | Unique four digit identifier
| role | CharField | Either "Admin" or "Employee"
| password |  CharField | passoword with min length of 6

## Table
| Field | Type | Description |
|--|--|--|
| table_number | IntegerField | Unique Table number in the restaurant
| num_seats | IntegerField  | The number of seats in the range 1-12
## Reservation
| Field | Type | Description |
|--|--|--|
| start_time | DateTimeField |the start date of the reservation 
| End_time | DateTimeField  |the end date of the reservation
| table | Foreign Key  | The table associated with the reservation
