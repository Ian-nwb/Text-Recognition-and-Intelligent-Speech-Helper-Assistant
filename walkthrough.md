# Docker Setup Walkthrough

This workspace is configured with separate Docker Compose environments for each project service. They connect via a shared Docker network (`app-network`) and use non-standard host ports to prevent port conflicts with any services running natively on your local computer.

---

## Workspace Layout

- **Database Layer**: Configuration in [infra/docker-compose.yml](infra/docker-compose.yml) (MongoDB & Mongo Express).
- **Backend API**: [server/Dockerfile](server/Dockerfile) and [server/docker-compose.yml](server/docker-compose.yml).
- **React Frontend**: [web/Dockerfile](web/Dockerfile) and [web/docker-compose.yml](web/docker-compose.yml).
- **Flutter Web Client**: [app/Dockerfile](app/Dockerfile) and [app/docker-compose.yml](app/docker-compose.yml).

---

## Port Mappings & Network Map

To ensure no host-side port collisions occur, the services are mapped to the following host ports:

| Service Component | Container Port | Host Port | Web Access Address / Connection String |
|---|---|---|---|
| **MongoDB** | `27017` | `27018` | `mongodb://root:examplepassword@localhost:27018` |
| **Mongo Express (GUI)** | `8081` | `8082` | `http://localhost:8082` |
| **Backend Express API** | `3000` | `3005` | `http://localhost:3005` |
| **React Frontend Client** | `80` | `8080` | `http://localhost:8080` |
| **Flutter Web Client** | `80` | `8081` | `http://localhost:8081` |

```
                     +---------------------------------------+
                     |             Your Local PC             |
                     +---------------------------------------+
                        |      |          |       |       |
                 Port   | Port |     Port |  Port |  Port |
                27018   | 8082 |     3005 |  8080 |  8081 |
                        v      v          v       v       v
      +---------------------------------------------------------------+
      |                        Docker Engine                          |
      |                                                               |
      |  [shared: app-network]                                        |
      |  +--------------------+      +-----------------------------+  |
      |  | mongodb            | <--->| backend                     |  |
      |  | (port 27017)       |      | (port 3000)                 |  |
      |  +--------------------+      +-----------------------------+  |
      |            ^                                                  |
      |            | (internal admin link)                            |
      |            v                                                  |
      |  +--------------------+      +-----------------------------+  |
      |  | mongo-express      |      | frontend (React)            |  |
      |  | (port 8081)        |      | (port 80)                   |  |
      |  +--------------------+      +-----------------------------+  |
      |                              +-----------------------------+  |
      |                              | mobile-web (Flutter)        |  |
      |                              | (port 80)                   |  |
      |                              +-----------------------------+  |
      +---------------------------------------------------------------+
```

---

## Step-by-Step Execution Guide

Because the backend and web services rely on the shared `app-network` (which is created by the database layer), you should boot the database containers first:

### 1. Run the Database (MongoDB & Mongo Express)
Navigate to the `infra` folder and spin up the services:
```bash
cd infra
docker compose up -d
```
* **Local Compass Connection**: Open your local **MongoDB Compass** application and connect to:
  `mongodb://root:examplepassword@localhost:27018`
* **Mongo Express Dashboard**: Open your browser and go to:
  `http://localhost:8082`

### 2. Run the Express Backend
Navigate to the `server` folder and spin up the container (it builds the app automatically):
```bash
cd ../server
docker compose up --build -d
```
* The API will now listen on:
  `http://localhost:3005`
* It communicates internally with the DB using `mongodb://mongodb:27017` over the shared network.

### 3. Run the React Web Frontend
Navigate to the `web` folder and run the container:
```bash
cd ../web
docker compose up --build -d
```
* The React application is built and served via Nginx on:
  `http://localhost:8080`

### 4. Run the Flutter Web Client
Navigate to the `app` folder and build/run the web container:
```bash
cd ../app
docker compose up --build -d
```
* The Flutter web bundle is built and served via Nginx on:
  `http://localhost:8081`
