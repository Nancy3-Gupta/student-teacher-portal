# Student Performance & Curriculum Tracker

A full-stack web application for teachers to manage student marks and curriculum progress. This project uses FastAPI, PostgreSQL, and Docker for a containerized environment.

##  Setup Instructions for Users

To run this project on your local machine, follow these steps:

### 1. Prerequisites
* **Docker Desktop** installed and running.
* **PostgreSQL 18** (or any recent version) installed locally on your machine.

### 2. Database Configuration
1. Open **pgAdmin 4**.
2. Create a new database named `curriculum_db`.
3. Note your PostgreSQL password.

### 3. Environment Setup
Since the database password is kept private for security, you must create your own configuration file:
1. In the root project folder, create a new file named `.env`.
2. Copy and paste the following lines into the `.env` file:
   ```text
   DB_USER=postgres
   DB_PASSWORD=YOUR_ACTUAL_PGADMIN_PASSWORD
   DB_HOST=host.docker.internal
   DB_NAME=curriculum_db