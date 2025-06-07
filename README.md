# Python REST API & Database Management Demo

### Overview

[cite_start]While my primary focus in recent years has been on Engineering Leadership and architecting large-scale enterprise systems, I remain deeply technical and hands-on. [cite_start]This project serves as a practical demonstration of my full-stack development capabilities, specifically using Python to build a scalable and containerized web application.

This application serves as a clean example of backend development best practices, including RESTful API design, database modeling with an ORM, and containerized deployment. [cite_start]It reflects the core software engineering principles I've applied and managed throughout my career.

### Key Features

* [cite_start]**RESTful API Architecture:** Designed with clean, resource-oriented endpoints for creating, retrieving, updating, and deleting data.
* [cite_start]**ORM & Database Integration:** Utilizes an ORM to effectively model data and interact with a PostgreSQL database, a skill I've applied with both SQL (Postgres) and NoSQL (MongoDB, Cassandra) systems.
* **Containerized for Portability:** Includes a `Dockerfile`, allowing the application and its dependencies to be built and run reliably in any environment. [cite_start]This aligns with my experience in driving containerization efforts using Docker and OpenShift.
* [cite_start]**Scalable Service Design:** Built as a microservice, a concept I have architected and implemented extensively using frameworks like Spring Boot.

### Technology Stack

* [cite_start]**Backend:** Python, Flask 
* [cite_start]**Database:** PostgreSQL 
* **ORM:** SQLAlchemy (or similar)
* [cite_start]**Deployment:** Docker 

This stack was chosen for its robustness, rapid development capabilities, and strong community support, making it ideal for a wide range of web services.

### Getting Started

To run this application locally using Docker, please ensure you have `Docker` and `docker-compose` installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/amiralig/split-repo-pub.git](https://github.com/amiralig/split-repo-pub.git)
    cd split-repo-pub
    git checkout georgian-demo3
    ```

2.  **Run with Docker Compose:**
    *(Note: You may need to create a `docker-compose.yml` file if one doesn't exist. A sample is provided below.)*

    ```bash
    docker-compose up --build
    ```
    The application should now be running and accessible.

---
#### Sample `docker-compose.yml`

If this project does not already contain a `docker-compose.yml` file, you can create one with the following content:

```yaml
version: '3.8'
services:
  web:
    build: .
    command: python app.py  # Or your specific run command
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    depends_on:
      - db
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydatabase
volumes:
  postgres_data:
