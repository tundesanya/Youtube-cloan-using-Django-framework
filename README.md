# vosynverse-backend

This repository is to store any code, README or other files made by the backend team.

## Readme Files
- [Tech Stack & Tools](readme_files/Tech_Stack_Tools.md)
- [Names & Syntax](readme_files/Nomenclature_Syntax.md)
- [Model Documentation](readme_files/Models_Docs.md)

# Local Environment Setup
### Django Project Setup
1. Clone this repository
2. Create a virtual environment
    > python -m venv .venv
3. Activate the virtual environment (Windows PowerShell)
    > .venv\Scripts\activate
4. Install the required packages
    > pip install -r requirements.txt


### PostgreSQL Database Setup and Configuration
1. Install PostgreSQL along pgAgent (using Stack Builder),
2. Login in the SQL Shell as superuser (psql) [[1]](https://docs.djangoproject.com/en/4.2/ref/databases/#optimizing-postgresql-s-configuration) [[2]](https://djangocentral.com/using-postgresql-with-django/) and then run the following:
    ```sql
    CREATE DATABASE vosynverse_db;
    CREATE USER vvuser WITH ENCRYPTED PASSWORD 'development-env-password';

    <!-- Optimizing PostgreSQL's Configuration-->
    ALTER ROLE vvuser SET client_encoding TO 'utf8';
    ALTER ROLE vvuser SET default_transaction_isolation TO 'read committed';
    ALTER ROLE vvuser SET timezone TO 'UTC';

    <!-- GRANT ALL PRIV.. might not be needed if we are changing the owner but I haven't checked -->
    GRANT ALL PRIVILEGES ON DATABASE vosynverse_db TO vvuser;
    ALTER DATABASE vosynverse_db OWNER TO vvuser;

    <!-- Need to be able to create databases for testing -->
    ALTER USER vvuser CREATEDB;
    ```
3. Use or copy the config/config.ini.example file to create a config.ini file in the same directory
4. Edit the config.ini file to match the database name, user and password created in the previous steps (or copy the below example for now)
    - config.ini:
        ```ini
        [Django]
        SECRET_KEY = django-insecure-k-mdzug-&s-^@d3*#+2mymwp^z^j@0!ivwrt*e4g10=(ge0+yf
        DEBUG = True
        ALLOWED_HOSTS = *

        [PostgreSQL]
        DBNAME = vosynverse_db
        HOST = localhost
        PORT = 5432
        USER = vvuser
        PASSWORD = development-env-password
        ```

### Django Project Setup Continued
1. Migration
    > python manage.py migrate
2. Run the server for testing
    > python manage.py runserver
3. Run the tests
    > python manage.py test


## Expected Starting Project Structure

Note: (might not be updated)
```
vosynverse-backend [root / this folder]
├── .venv [ignored in git]
│   └── ... [virtual environment files]
├── config
│   ├── config.ini
│   └── config.ini.example
├── readme_files
│   └── ... [readme files]
├── vv_backend
│   ├── content
│   │   └── ... [content app files]
│   ├── user_interactions
│   │   └── ... [user_interactions app files]
│   ├── users
│   │   └── ... [users app files]
│   ├── vv_backend
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
├── .gitignore
├── README.md
└── requirements.txt
```