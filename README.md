#  EPAM Python Project – Project Management API

A backend service for managing projects, documents, and user access, built with **FastAPI**, **PostgreSQL**, and **AWS S3/Lambda integration**.

---

##  Overview

This project implements a **project management system** where users can:

- Authenticate using JWT
- Create and manage projects
- Upload and manage documents (PDF, DOCX)
- Share projects with other users
- Store files in S3-compatible storage
- Process file-related events using AWS Lambda

---

##  Tech Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Docker & Docker Compose
- AWS S3 / MinIO (local development)
- AWS Lambda
- JWT Authentication
- Pydantic validation
- GitHub Actions (CI)

---

##  Project Structure


app/

├── api/

├── core/

├── db/

├── schemas/

├── services/

└── main.py

lambda/

└── project_size/

tests/
docker-compose.yaml
pyproject.toml


---

##  Authentication

- JWT-based authentication
- Token issued via `POST /login`
- Token validity: **1 hour**
- All protected endpoints require:


Authorization: Bearer <token>


---

##  Architecture Diagram

```mermaid
flowchart TD
    A[Client / User] --> B[FastAPI Application]

    B --> C[Auth Router]
    B --> D[Projects Router]
    B --> E[Documents Router]

    C --> F[JWT Authentication]
    D --> G[Project Service]
    E --> H[Document Service]

    G --> I[(PostgreSQL)]
    H --> I[(PostgreSQL)]

    H --> J[Storage Layer]
    J --> K[Local Storage / MinIO / AWS S3]

    K --> L[AWS Lambda / S3 Event Trigger]
    L --> M[Project Size Calculation]

    B --> N[Pydantic Schemas]
    B --> O[Dependencies / Access Control]
    ```

## API Endpoints

Auth

POST /auth – Register user

POST /login – Login and receive JWT

##Projects

POST /projects – Create project

GET /projects – List user-accessible projects

GET /project/{id}/info – Get project details

PUT /project/{id}/info – Update project

DELETE /project/{id} – Delete project

## Documents

GET /project/{id}/documents – List documents

POST /project/{id}/documents – Upload document

GET /document/{id} – Download document

PUT /document/{id} – Update document

DELETE /document/{id} – Delete document

## Sharing

POST /project/{id}/invite?user=<login>


POST /project/{id}/share?email=<email> (optional)
## Storage & File Handling
AWS S3 (production)
MinIO (local)

Supported:

PDF
DOCX

## AWS Lambda Integration
Triggered on S3 events
Calculates total project file size

Extendable for image processing
##Running Locally
git clone https://github.com/ToroRossoLGD/EPAM-python-project
cd EPAM-python-project

Create .env:

DB_HOST=db
DB_USER=postgres
DB_PASS=postgres
DB_NAME=postgres

SECRET_KEY=your_secret_key

Run:

docker-compose up --build

Swagger:
http://localhost:8000/docs

## Testing
pytest

## CI/CD
GitHub Actions
Lint + tests

Author

Uroš Jović