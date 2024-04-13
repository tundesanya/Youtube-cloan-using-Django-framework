# Django + PostgreSQL Starting Setup (Windows 10)

#### Django Setup
- Create the virtual environment
    > python3 -m venv .venv
- Activate the virtual environment
    > .\\.venv\Scripts\Activate.ps1
- Install the requirements
    > pip install -r requirements.txt
    
    Note: Remember to pip freeze when development has reached a good point.

#### Django Project Setup
- Create the project
    > django-admin startproject project_name
- Renamed the project folder to project_name_backend (Optional)
- Create the app
    > python manage.py startapp project_app_name (could be same as project_name)

#### PostgreSQL Setup:
- Installed pgAgent using Stack Builder (provided by PostgreSQL) (Mostly Optional)
- Note: Restart of postgresql service might be required.
- In SQL Shell as superuser (psql) [[1]](https://docs.djangoproject.com/en/4.2/ref/databases/#optimizing-postgresql-s-configuration) [[2]](https://djangocentral.com/using-postgresql-with-django/):
    ```sql
    CREATE DATABASE project_name_db;
    CREATE USER project_user WITH ENCRYPTED PASSWORD '<PASSWORD>';
    
    <!-- Optimizing PostgreSQL's Configuration-->
    ALTER ROLE project_user SET client_encoding TO 'utf8';
    ALTER ROLE project_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE project_user SET timezone TO 'UTC';
    
    <!-- GRANT ALL PRIV.. might not be needed if we are changing the owner but I haven't checked -->
    GRANT ALL PRIVILEGES ON DATABASE project_name_db TO project_user;
    ALTER DATABASE project_name_db OWNER TO project_user;
    ```
- Made the following files in C:\Users\USER\AppData\Roaming\postgresql (i.e. %APPDATA%\postgresql)
    - .pg_service.conf
        ```ini
        [service-name]
        host=localhost
        port=5432
        dbname=project_name_db
        user=project_user
        ```
    - pgpass.conf
        ```
        # hostname:port:database:username:password
        localhost:5432:project_name_db:project_user:<PASSWORD>
        localhost:5432:postgres:postgres:<PASSWORD>
        ```
- In settings.py:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {
                'service': 'service-name',
                # Can't figure out why the absolute path was needed for below passfile.
                'passfile': 'C:/Users/USER/AppData/Roaming/postgresql/pgpass.conf'
            }
        }
    }
    ```

#### Django Project Setup (contd.)
- Migrate
    > python manage.py migrate

---