# PostgreSQL Monitoring Application

This project monitors PostgreSQL databases, providing insights into activity, performance, object sizes, and locks.

## Structure
- `backend/` — FastAPI backend, database models, API endpoints, and snapshot service.
- `frontend/` — React + TypeScript frontend application using Material-UI.
- `docker-compose.yml` — Orchestrates the backend, frontend, and the monitoring PostgreSQL database.
- `.env.example` — Template for environment variables.

## Features
- Monitor multiple PostgreSQL instances securely.
- Visualize session activity over time.
- Browse database objects and their sizes.
- Identify locks and blocking sessions.
- Analyze query performance with `pg_stat_statements` (if enabled on the monitored instance).
- Modern, responsive UI with charts and tables.

## Architecture Overview
The application consists of several components:
1.  **FastAPI Backend**: Handles API requests, manages database connections (for monitored instances), interacts with the monitoring database, and runs the snapshot scheduler. Uses SQLAlchemy for ORM and `asyncpg` for connecting to monitored databases.
2.  **React Frontend**: Provides the user interface for managing connections and viewing monitoring data. Built with Vite, TypeScript, and Material-UI.
3.  **PostgreSQL Monitoring Database**: Stores connection details (securely hashed passwords) and historical monitoring data collected by the snapshot service. This is a separate PostgreSQL instance managed by Docker Compose.
4.  **APScheduler (within Backend)**: Periodically connects to each monitored PostgreSQL instance, collects statistics (`pg_stat_activity`, `pg_stat_statements`, object sizes, locks), and stores snapshots in the monitoring database.

## Getting Started

### Prerequisites
- Docker ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose ([Install Docker Compose](https://docs.docker.com/compose/install/))

### Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd postgres-monitor2
    ```
2.  **Set up environment variables:**
    - Copy the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Edit the `.env` file and configure the variables, especially the `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` for the *monitoring* database that will store the collected data. You can leave the defaults if running locally for the first time.
      ```dotenv
      # Monitoring Database Connection (used by backend & migrations)
      DATABASE_URL=postgresql+asyncpg://user:password@db:5432/monitor_db

      # Settings for the PostgreSQL container *itself* (used by docker-compose)
      POSTGRES_DB=monitor_db
      POSTGRES_USER=user
      POSTGRES_PASSWORD=password

      # Backend API settings
      SECRET_KEY=your_very_secret_key_here # CHANGE THIS FOR PRODUCTION
      ALGORITHM=HS256
      ACCESS_TOKEN_EXPIRE_MINUTES=30

      # Add other necessary variables if any (e.g., frontend API base URL if needed)
      ```
    - **Important:** Ensure the `DATABASE_URL` components match the `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and the service name (`db`) defined in `docker-compose.yml`. The `SECRET_KEY` should be changed to a strong, random string for any non-local deployment.

3.  **Build, Run, and Migrate (Option 1: Automated Script):**
    For the first time setup, you can use the provided script which handles building, starting services, waiting for the DB, and applying migrations:
    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

4.  **Build, Run, and Migrate (Option 2: Manual Steps):**
    Alternatively, run the steps manually:
    a.  **Build and Run with Docker Compose:**
        ```bash
        docker-compose up --build -d
        ```
        This command builds the images for the backend and frontend (if they don't exist or have changed) and starts all the services (backend, frontend, monitoring database) in detached mode.

    b.  **Apply Database Migrations:**
        Before the application can function correctly, you need to apply the database migrations to set up the necessary tables in the monitoring database.
        ```bash
        docker compose exec backend alembic upgrade head
        ```
        *Wait a few seconds after the `up` command for the database service (`db`) to initialize before running this.*

5.  **Access the Application:**
    - **Frontend:** Open your web browser and navigate to `http://localhost:5173` (or the port mapped for the `frontend` service in `docker-compose.yml`).
    - **Backend API Docs (Swagger UI):** Navigate to `http://localhost:8000/docs` (or the port mapped for the `backend` service).

### Initial Use
1.  **Add a Connection:** Navigate to the "Connections" page in the frontend. Click "Add Connection" and fill in the details for the PostgreSQL instance you want to monitor. Credentials are required to connect and gather statistics.
2.  **View Data:** Once a connection is added, the snapshot service will start collecting data periodically. Explore the "Activity", "Objects", and "Locks" pages to view the monitored information. Data will populate over time as snapshots are taken.

## Development
- **Backend:** Located in the `backend/` directory. Uses FastAPI, SQLAlchemy, Alembic for migrations, and APScheduler.
- **Frontend:** Located in the `frontend/` directory. Uses React, TypeScript, Vite, and Material-UI.

### Running Tests (Example - Adjust as needed)
```bash
# Backend tests (example, assuming pytest setup)
docker-compose exec backend pytest

# Frontend tests (example, assuming vitest/jest setup)
docker-compose exec frontend npm run test
```

---

See `IMPLEMENTATION_PROGRESS.md` for the detailed implementation status.
