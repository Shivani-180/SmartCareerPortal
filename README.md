Smart Career Development and Skill Enhancement Portal

About the Project:

The Smart Career Development and Skill Enhancement Portal is a web-based academic project designed to support students in managing their profiles and skills and exploring career development. The project uses a Python Flask backend, a web-based interface, and an SQLite database.

Project Objectives:

- Provide a centralized platform for student profile management.
- Enable secure user registration and login.
- Store and manage student information.
- Provide a foundation for career and skill development.

Implemented Features:

- User registration with duplicate-email checking.
- Password hashing for account security.
- Login and session-based authentication.
- Protected student dashboard.
- Student profile display and editing.
- Logout functionality.
- SQLite database integration.

Technologies Used:

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Database: SQLite
- Templating: Jinja2
- Database ORM: SQLAlchemy, if included in the current implementation

Project Structure:

- "app.py" — Main Flask application and routes.
- "models.py" — Database model definitions.
- "requirements.txt" — Python package dependencies.
- "static/" — Static assets, if present.
- "templates/" — HTML templates, if present.

Installation and Setup:

Prerequisites

- Python installed on your computer.
- Git installed if cloning the repository.
- A terminal or command prompt.

Steps:

1. Clone the repository:
   
   git clone
   https://github.com/Shivani-180/SmartCareerPortal

3. Open the project directory:
   
   cd SmartCareerPortal

4. Create a virtual environment:
   
   python -m venv venv

5. Activate it on Windows:
   
   venv\Scripts\activate

6. Install the project dependencies:
   
   pip install -r requirements.txt

7. Start the application:
   
   python app.py

8. Open your web browser and visit "http://127.0.0.1:5000" to access the application, if this is the address configured in "app.py".

Future Enhancements

Potential enhancements include expanded skill assessments, skill-gap analysis, career and learning recommendations, progress tracking, and career readiness reporting.

Project Type

Academic web application project.
