# E-learning-App

## Project Title: MOOC E-Learning Platform Backend API

-  Description:
This repo offers a Learning Management System (LMS) delivered as RESTful backend API designed for a modern e-learning platform, built with FastAPI. It supports user authentication and role-based access control for students, teachers, and administrators, allowing seamless interaction with educational content. The API enables course creation, section and lesson management, user enrollment, and rating/review systems. It also includes automated documentation (Swagger/OpenAPI), secure token-based authentication, and a scalable PostgreSQL database setup, delivered through an external API integration with Supabase.


-------------------------------------------------------------------------


##  Table of Contents

- [About the Project](#about-the-project)
- [Team Members](#team-members)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Architecture Overview](#architecture-overview)
- [Database Design](#database-design)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Future Improvements / Roadmap](#future-improvements--roadmap)

---

## Team Members

- **Boris Tsonkov**
- **Petar Pavlov**
- **Dilyana Bozhinova**

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Postgresql
- **Tools & Libraries:** 
   - OAuth2  
   - JWT  
   - mailjet External API
   - Supabase External API
   - Google Auth External API
   - Cloudinary External API
   - python-dotenv  
   - PostgreSQL  
   - Pydantic  
   - Uvicorn
   - Pytest   


---

## Features

###  Authentication

- **User Registration**
  - Students and teachers can register using their email and password. Teachers receive email verification links as well as await admin approval.
- **User Login**
  - Email and password-based login returns a JWT token. Supports OAuth2 login via Google.
- **Google Authentication**
  - Users can log in with their Google accounts. If a matching account doesn’t exist, one is created automatically.

###  Admin Access

- **Manage User Accounts**
  - Admins can activate or deactivate teacher/student accounts and approve teacher registrations.
- **View and Filter Courses**
  - Admins can search and filter courses by title, teacher, or student.
- **Moderate Enrollments**
  - Admins can remove students from courses.
- **Deprecate Courses**
  - Admins can soft-delete courses and trigger email notifications to enrolled students.

###  Teacher Portal

- **Manage Profile**
  - Teachers can view and update their account info, including LinkedIn and phone number.
- **Create and Manage Courses**
  - Teachers can create, update, or deactivate their own courses, including adding/hiding course sections.
- **Enrollment Approval**
  - Teachers receive enrollment requests and can approve them manually.
- **Student Report Generation**
  - Teachers can generate reports of enrolled students across their courses.


###  Student Portal

- **View and Edit Profile**
  - Students can update personal details and upload avatar images.
- **Course Enrollment**
  - Students can enroll in free or premium courses. Premium enrollments are limited to 5 unless all are completed or canceled.
- **Track Course Progress**
  - Students can mark sections as completed and track progress per course.
- **Course Rating**
  - Students can rate courses they've enrolled in or completed.
- **Course Completion**
  - Students can complete a course only if all its sections are marked as completed.

###  Courses & Content
-  **Public and Private Course Listings**
  - Unauthenticated users can browse public courses. Authenticated students with premium access can see more.
-  **Sections Management**
  - Teachers can add, update, or hide sections in their courses.
-  **Role-Based Access to Sections**
  - Admins and course owners can always view sections; students can view only if enrolled.

---

## Installation

1. **Clone the repository:**  
   `git clone https://github.com/Forum-App-web-module/E-learning-App.git`

2. **(Optional, Recommended) Create and activate a virtual environment:**  
   `python -m venv venv`  
   `.venv\Scripts\activate.ps1` 

3. **Install the required dependencies:**   
   `pip install -r requirements.txt`  
   *If additional dependency is installed use the bellow command to update the file*  
   *pip freeze > requirements.txt*

4. **Set up your environment variables:**
    Repository includes template .env file. Copy `.env.example` to `.env` and fill in your own credentials:

6. **Run the application**:  
   `uvicorn main:app --reload`  
   *Use `--port {port_number}` if you want to run the app on a different port (default is `8000`)*

## Architecture Overview

## Database Design

![Database Schema](docs/misc/E-Learning%20DB%20diagram%20snapshot.png)

### The schema covers the following key entities
**Color Legend**:
- User entities - admins, teachers, students - in Bright Green
- Course entities - courses, course_sections - in Pink
- Composite tables - course_rating, student_course_sections - in Peach
- Subscribtion-related - enrollments, subscriptions - in lighter green
- Other - external_resources, event_log - in default white 


## N-Tier Architecture  

- **View** - Client/UI
- **Controller** - Web Server and Application/Business Logic
- **Model** - Data and Database Layers

![System Architecture](docs/misc/system_architecture%20_diagram.png)

Through the FastAPI server, the client calls the routers which interact with Security and Service Layers.  
The two services on their side, use the Pydantic models and interact with the Database via Database Connector.


## API Documentation
Refer to the FastAPI swagger for the backend API docs. - http://127.0.0.1:8000/docs

## Testing
   The tests are written using the `pytest` framework.
   All tests are located in E-LEARNING-APP/tests/  
### Coverage:  
Service and Repo Layers for:
   - admin
   - course
   - enrollment
   - student
   - teacher
   - user

### Tests execution:  
    - GitHub Action - https://github.com/Forum-App-web-module/E-learning-App/actions/workflows/test.yml

## Future Improvements / Roadmap
- Develop a log event feature for user timelines, admin actions, and system event captions.
- Develop a personal messaging feature with encrypted messages.
- Implement a personal notes feature.
- Add endpoints for user event history.
- Continue developing email notifications:
- New course advertisements
- Action reminder emails


---

