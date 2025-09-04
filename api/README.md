# BAES Flask Application with MSSQL

This project contains a Flask application containerized with Docker, connected to a Microsoft SQL Server 2017 database.

## Project Structure

- `api/`: Directory containing all API-related code
  - `app.py`: The Flask application
  - `models/`: Directory for database models
  - `routes/`: Directory for API routes
  - `templates/`: Directory for HTML templates
  - `static/`: Directory for static assets (CSS, JS, images)
- `Dockerfile`: Instructions for building the Flask application container
- `docker-compose.yml`: Configuration for orchestrating the Flask and MSSQL containers
- `init-db.sql`: SQL script to initialize the database user
- `mssql-entrypoint.sh`: Entrypoint script for the MSSQL container
- `pyproject.toml`: Python project dependencies

## Prerequisites

- Docker
- Docker Compose

ODBC Driver 17: https://go.microsoft.com/fwlink/?linkid=2266337
Or : https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17

## Getting Started

1. Clone the repository
2. Navigate to the project directory
3. Build and start the containers:

```bash
docker-compose up -d
```

This will:
- Start a MSSQL 2017 container
- Create a user (username: Externe, password: Secur3P@ssw0rd!)
- Display a confirmation message when the database initialization is complete
- Start the Flask application container
- Connect the Flask application to the MSSQL database

## Accessing the Application

- Flask application: http://localhost:5000
- Database connection test: http://localhost:5000/db-test

## Database Connection Details

- Host: localhost (or mssql from within the Docker network)
- Port: 1433
- Username: Externe
- Password: Secur3P@ssw0rd!
- Database: master

## Stopping the Application

To stop the containers:

```bash
docker-compose down
```

To stop the containers and remove the volumes (this will delete all database data):

```bash
docker-compose down -v
```

## Development

To make changes to the application:

1. Modify the code as needed
2. Rebuild and restart the containers:

```bash
docker-compose up -d --build
```
