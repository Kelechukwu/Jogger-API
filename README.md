**Getting Started**

This application can be run either of two ways 
1. **Using docker / docker-compose ( Make sure you have docker installed locally)**
   - from the project directory run 
   `docker-compose build && docker-compose up -d`
   - this should setup containers for the server and database(this application uses postgres DB). The application should start running on [localhost:8000](http://127.0.0.1:8000)
   - to run tests execute `docker exec -it fitness-service pipenv run python manage.py test --noinput --verbosity 2`
2. **Running directly but using a Docker Postgres GIS image.**
   - from the project directory run 
     `docker-compose build db && docker-compose up -d db`
   - now `cd fitness_jogger` to enter the application root directory
   - make sure you have _pipenv_ installed run `pipenv install` to install all requirements
   - apply migrations `pipenv run python manage.py migrate`
   - start the server `pipenv run python manage.py runserver`


**WorkFlow**
  - **Create a regular account** 

```
POST /signup
    {
      "email": "test@test.com",
      "password": "qwerty1234"
    }
```
Take the access token in the response.Add it as Bearer token in subsequent requests.
_**NOTE**: to create the first admin user you have to do that via the console,
and to give another user admin or manager access, this has to be done_

  - Create superuser run pipenv run 
 `python manage.py createsuperuser` or 
 `docker exec -it fitness-service python manage.py createsuperuser `
  - To give a regular user higher access send a POST as admin user and edit role value of any user to 1 

  - **Login / Authenticate** 

```
 POST /login
       {
    	"email": "test@test.com",
    	"password": "qwerty1234"
      }
```
- **View (GET) or edit(POST) all Users or a Single User info as Admin**
  
```
Header Authorization: Bearer eyJ0eXAiOiJ ….

GET / POST / DELETE users/<user_id>
```
- **Jogging Data**
  - **CRUD Jogs as Admin**
```
Header Authorization: Bearer token ….

GET POST DELETE /jogs/<jog_id>
```
  - **CRUD Personal Jogging Data** 
```
Header Authorization: Bearer token ….

GET POST DELETE /myjogs/<jog_id>
```
  - **Query Personal Jogging Data** 
```
Header Authorization: Bearer token ….

GET /myjogs?q=((distance gt 400) AND (date gt '2020-05-04'))
    /myjogs?q=(location eq 'POINT {34 2}')
```

  - **Get Weekly Report Jogging Data** 
  **Note**: user_id is compulsory.
```
Header Authorization: Bearer token ….

GET weekly_report/<user_id>?date=2020-11-27
```




