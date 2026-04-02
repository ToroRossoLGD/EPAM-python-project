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
├── api/ # API routers (auth, projects, documents)
├── core/ # Config, security, dependencies
├── db/ # Database models and session
├── schemas/ # Pydantic schemas
├── services/ # Business logic & storage layer
└── main.py # Entry point

lambda/
└── project_size/ # AWS Lambda function (calculate project size)

tests/ # Unit & integration tests
docker-compose.yaml # Docker services
pyproject.toml # Tooling (ruff)


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

 ##  API Endpoints
Auth
POST /auth – Register user
POST /login – Login and receive JWT
Projects
POST /projects – Create project
GET /projects – List user-accessible projects
GET /project/{id}/info – Get project details
PUT /project/{id}/info – Update project
DELETE /project/{id} – Delete project
Documents
GET /project/{id}/documents – List documents
POST /project/{id}/documents – Upload document
GET /document/{id} – Download document
PUT /document/{id} – Update document
DELETE /document/{id} – Delete document
Sharing
POST /project/{id}/invite?user=<login> – Grant access
POST /project/{id}/share?email=<email> – Send invite link (optional)
    ## Storage & File Handling
Files are stored using:
AWS S3 (production-ready)
MinIO (local development)
Supported file types:
.pdf
.docx
File validation:
Size limits enforced per document
## AWS Lambda Integration

Lambda function triggers on S3 events:

Calculates total size of project files
Can be extended to:
Image processing (resize, optimization)
 Running Locally
1. Clone repository
git clone https://github.com/ToroRossoLGD/EPAM-python-project
cd EPAM-python-project
2. Create .env file
DB_HOST=db
DB_USER=postgres
DB_PASS=postgres
DB_NAME=postgres

SECRET_KEY=your_secret_key
3. Run with Docker
docker-compose up --build
## API Access

Swagger UI:

http://localhost:8000/docs
## Testing

Run tests:

pytest

## CI pipeline includes:

Linting (Ruff)
Tests (pytest)
CI/CD

## Current setup:

GitHub Actions:
Install dependencies
Run lint checks
Execute tests

Planned improvements:

Docker build & push
Automated deployment
## Architecture Notes
Layered architecture:
API → Services → Database
Separation of concerns
Storage abstraction (local vs S3)
Access control via project_access table

## Future Improvements
Improve CI/CD pipeline
Implement denormalization strategies

Author

Uroš Jović