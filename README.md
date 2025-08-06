Berar App Django Project

------------------------

Project Overview

Berar App is a modular Django backend project built with Django 5.2 and Django REST Framework,
designed to manage multiple systems via dedicated apps:

Apps and Descriptions:

 auth_system: User authentication, login, registration, and token management.
- cms: Customer Management System for managing customer data, interactions, and related content.
- ems: Employee Management System, handling employee records.
- lead: Lead and enquiry management, loan processing workflows.
- dedup: Used for setting remarks for existing customers. 
- code_of_conduct: Used for uploading multiple files and storing these records.

------------------------

Environment Setup

1. Create and Activate Virtual Environment

Windows:
  python -m venv venv
  .\venv\Scripts\activate

Mac/Linux:
  python3 -m venv venv
  source venv/bin/activate

2. Install Dependencies

Make sure you have requirements.txt, then run:
  pip install -r requirements.txt

If you don’t have requirements.txt yet, generate it with:
  pip freeze > requirements.txt

3. PostgreSQL Setup

Ensure PostgreSQL is installed and running.

Create the project database:
  psql -U postgres -c "CREATE DATABASE db_berar_app;"

Update your Django settings.py with your DB credentials.

4. Run Migrations

Apply all migrations to setup DB schema:
  python manage.py makemigrations
  python manage.py migrate

If you get migration or table errors, try:
  python manage.py migrate --fake
  python manage.py migrate

5. Seed Initial Data

Populate DB with default data, admin user, roles, etc.:
  python manage.py seed_all

6. Run the Development Server

Start server locally on port 9000:
  python manage.py runserver 9000

Test API:
  Visit http://127.0.0.1:9000/api/test/
  Expected response:
    {"message": "Main test API is working ✅"}

------------------------

Useful Management Commands

- python manage.py makemigrations    # Create migrations after model changes
- python manage.py migrate           # Apply migrations to database
- python manage.py seed_all          # Seed initial data (admin, roles, etc.)
- python manage.py fetch_location_data  # Populate city/location data
- python manage.py createsuperuser  # Create admin user manually

------------------------

Project Structure

berar_app/
├── auth_system/         # Authentication app
├── cms/                 # Customer Management System
├── dedup/               # Used for setting remarks for existing customers.
├── ems/                 # Employee management
├── lead/                # Lead and enquiry management
├── code_of_conduct/     # Used for uploading multiple files and storing these records.
├── berar/               # Project settings and URLs
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies list
└── README.md            # This documentation file

------------------------

Environment Variables

Use a .env file for environment settings, example:

SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=db_berar_app
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

Load them in settings.py with python-decouple or os.environ.

------------------------



------------------------

API EndpointsF

- GET /api/test/  
  Returns: {"message": "Main test API is working ✅"}

App APIs prefix: /api/{app_name}/

Examples:
- /api/auth_system/
- /api/cms/
- /api/ems/
- /api/lead/
- /api/dedup/
- /api/code_of_conduct/

Check each app's urls.py for specific endpoints.

------------------------

Development Tips

- Always activate your virtual environment before running commands.
- Keep requirements.txt updated with `pip freeze > requirements.txt`.
- Use `python manage.py runserver 0.0.0.0:9000` for remote access.
- Use Django Admin (/admin/) for quick data checks and user management.
- Run tests often to keep your code stable (if tests are available).

------------------------

Additional Notes

- For production, use WSGI/ASGI servers like Gunicorn or Daphne.
- Keep sensitive keys secure; don’t commit .env files.
- Document new apps/features in this README.
- Contact the maintainer for questions or contributions.

------------------------

License & Contact

Specify your license (e.g., MIT, GPL).

Contact info:
Email: your_email@example.com
GitHub: https://github.com/yourusername/berar_app

------------------------

Happy coding! 🚀
