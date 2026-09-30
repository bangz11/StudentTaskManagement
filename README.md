# Student Task Management System

A Django-based Student Task Management System for managing university assignments.

## Features

- Student registration
- Student login and logout
- Secure user authentication
- Personal assignment management
- Create assignments
- View assignments
- Edit assignments
- Delete assignments
- Search assignments
- Filter by status
- Filter by priority
- Sort assignments
- Student dashboard
- Assignment statistics
- Upcoming assignments
- Django admin
- RESTful API
- API authentication
- User ownership protection
- Responsive frontend

## Technologies

- Python
- Django
- Django REST Framework
- SQLite
- HTML
- CSS
- JavaScript

## Web Pages

- `/` - Home
- `/register/` - Register
- `/login/` - Login
- `/dashboard/` - Student dashboard
- `/assignments/` - Assignment list
- `/assignments/add/` - Add assignment
- `/admin/` - Django admin

## REST API

### List assignments

GET:

`/api/assignments/`

Requires authentication.

### Create assignment

POST:

`/api/assignments/`

### Get one assignment

GET:

`/api/assignments/<id>/`

### Update assignment

PUT or PATCH:

`/api/assignments/<id>/`

### Delete assignment

DELETE:

`/api/assignments/<id>/`

## Assignment Fields

- title
- subject
- description
- due_date
- priority
- status
- created_at
- updated_at

### Priority

- Low
- Medium
- High

### Status

- Pending
- In Progress
- Completed

## Security

The API requires authentication.

Users can only access assignments belonging to their own account.

## Testing

Run:

`python manage.py test`

Run the Django system check:

`python manage.py check`

## Run the Website

`python manage.py runserver`

Open:

`http://127.0.0.1:8000/`
