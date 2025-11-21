# Comprehensive Instrumentation Database 

## Project Objective
This project is a Django-based system designed for comprehensive management of industrial instrumentation. 
The main goal is to store, manage and track instrument information, including manufacturer, model, serial number, site location and calibration / maintenance records. 

## Technologies Used
--**Backend**: Django (Python)
-*# Ctabase**: Microsoft SQL Server
- **ORM**: Django ORM to manage SQL Server tables
- **Other Tools**: Git for version control, VS code for development

## Prerequisites 
1. Python 3.10 or higher **
2. Django 4.x **
3. Microsoft SQL Server **
4. ODBC Driver 17 or 18 for SQL Server **
5. Virtual Environment **(recommended)

## How to Set Up the Project 
1. Clone the repository:
'''bash
git clone https://github.com/sardaromran1/COMPREHENSIVE_INSTRUMENTATION_DATABASE.git
cd COMPREHENSIVE_INSTRUMENTATION_DATABASE/instrument_project

2. Create and activate a virtual environment
python-m venv env
# Windows 
env\Scripts\activate
# Linux / Mac
source env/bin/activate 

3. Install the required packages
pip install-r requirements.txt

4. Set environment variables for SQL Server connection:
* Create a.env file and add your database credentials
DB_NAME = YourDatabaseName
DB_USER = YourUserName
DB_PASSWORD = YourPassword
DB_PORT = 1433
* Use os.getenv. in settings.py to read these values.

5. Run the Django development server
Python manage.py runserver

6. Access the application
* Open your browser and go to:
http://127.0.0.1:8000/
* To access the Django admin panel:
http://127.0.0.1:8000/admin


## SQL Server Database Link
* The main database is hosted in SQL Server
* SQL files in the sql/ folder include table structures and can be executed to set up the database.

## Important Notes
* Make sure your SQL Server instance running and accessible from Django
* Never hardcode sensitive credentials; always use a.env file
* To modify or add new tables, update Django models and run migrations
