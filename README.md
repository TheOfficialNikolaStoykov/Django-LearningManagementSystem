# Django Learning Management System (LMS)

This project is a robust Learning Management System (LMS) built using Django. It offers essential functionalities for managing users (students, teachers, and administrators), courses, lessons, and related resources. The LMS supports user authentication, media uploads, and includes an admin interface for managing content.

## Features

### User Management
- User registration, login, and profile management.
- Supports roles: Admin, Teacher, and Student.
- Teachers and admins can manage courses, lessons, and sections.

### Course and Lesson Management
- Teachers can create, update, and delete courses.
- Sections can be added to courses to organize lessons.
- Teachers can upload lessons with video content.
  
### Media Uploads
- Supports uploading and managing images and videos for lessons.
- Wistia integration for video hosting.

### News and Announcements
- Teachers and staff members can post news.
  
### Authentication and Permissions
- Role-based access: Admins have full control, Teachers manage their courses, and Students can view their enrolled courses.
- Secure login/logout functionality.

### Admin Access
- Admins have access to manage all content, including courses, users, and news.
- Admin can manage course categories, lesson statuses, and student enrollments.

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Django 4.x or higher
- Virtual environment setup (venv)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/django-lms.git
    ```

2. Navigate to the project directory:

    ```bash
    cd django-lms
    ```

3. Set up a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Run migrations to set up the database schema:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser for accessing the Django admin:

    ```bash
    python manage.py createsuperuser
    ```

7. Start the Django development server:

    ```bash
    python manage.py runserver
    ```


### Running Tests

To run the test suite for the application:

```bash
python manage.py test
```

To run test coverage, use the following commands:

```bash
coverage run manage.py test
coverage report
```

## Technologies Used

- **Backend Framework:** Django
- **Media Handling:** Wistia API for video uploads
- **Authentication:** Django Authentication and Permission system
- **Database:** SQLite (can be replaced with other databases like PostgreSQL)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
