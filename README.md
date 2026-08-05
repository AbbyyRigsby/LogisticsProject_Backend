# Logistics Path Tracking API — Documentation

## 1. Overview

A Django REST Framework service that computes the shortest travel path between airports and seaports. On startup it loads airport/seaport datasets into a Pandas/GeoPandas dataframe, builds a **K-Nearest Neighbors graph** (via `sklearn.neighbors.BallTree`, haversine distance, k=10 by default) with NetworkX, and answers routing queries with Dijkstra's algorithm.

**Stack:** Django 5.2.10, Django REST Framework 3.16.1, NetworkX, GeoPandas, scikit-learn, Pandas, Docker.

---

## 2. Directory Structure

```
LogisticsProject_Backend/
├── dockerfile                      # Container build (installs GDAL system deps)
├── docker-compose.yaml             # web + postgres services
├── requirements.txt                # Python dependencies (UTF-8; add psycopg2-binary for Postgres)
├── .dockerignore
├── .gitignore
├── README.md
└── logisticsapi/                   # Django project root (contains manage.py)
    ├── manage.py
    ├── logisticsapi/               # Django settings module
    │   ├── settings.py             # DEBUG=True, Postgres via env vars, app 'api' registered
    │   ├── urls.py                 # root router → /admin/, /api/v1/
    │   ├── wsgi.py
    │   └── asgi.py
    └── api/                        # Main application ("api")
        ├── apps.py                 # builds the graph once at app startup (AppConfig.ready)
        ├── models.py                # Path model (origin, destination, distance_km)
        ├── serializers.py           # NodeDetailSerializer, LogisticsPathSerializer, PortListSerializer
        ├── views.py                 # api_root, ShortestPathView, PortsListView
        ├── urls.py                  # /api/v1/ sub-routes
        ├── admin.py
        ├── tests.py
        ├── migrations/
        │   └── 0001_initial.py      # creates the Path table
        └── functions/
            ├── graph_setup.py       # loads CSVs, builds the KNN graph
            └── shortest_path.py     # Dijkstra lookup + response shaping
```

Key thing to know: the graph is built **once**, when the Django app starts (`ApiConfig.ready()` in `apps.py`), and cached in memory on the app config object (`apps.get_app_config('api').graph`). It is not rebuilt per-request.

---

## 3. Installation & Setup

### 3.1 Prerequisites

- Docker + Docker Compose (recommended path), **or** Python 3.11 with GDAL system libraries installed locally (`binutils`, `libproj-dev`, `gdal-bin`, `libgdal-dev`, `python3-gdal` — needed for GeoPandas/`pyogrio`/`pyproj`).
- Your own airport and seaport datasets (this repo does not ship them — see below).

### 3.2 Prepare the datasets

The graph builder (`graph_setup.py`) expects two **semicolon-delimited (`;`)** CSV files, one for airports and one for seaports, each with at minimum these columns:

| column | type | notes |
|---|---|---|
| `name` | string | used as the graph node ID and in API responses |
| `latitude` | float | |
| `longitude` | float | |
| `country_code` | string | |

Download/export your airport and seaport datasets (e.g. from OpenFlights, World Port Index, or similar external sources) into this format, and place them somewhere inside the repo, e.g.:

```
LogisticsProject_Backend/
└── data/
    ├── airports.csv
    └── seaports.csv
```

> **Path resolution detail:** `graph_process()` resolves the base directory as **four levels up** from `graph_setup.py`, which lands on the repository root (the same folder as `dockerfile`). So the env vars below should be paths **relative to the repo root**, e.g. `data/airports.csv`.

### 3.3 Configure environment variables

Create a `.env` file at the **repo root** (same level as `dockerfile` and `docker-compose.yaml` — `docker-compose.yaml` explicitly loads it via `env_file`):

```env
AIR_DATASET=data/airports.csv
SEA_DATASET=data/seaports.csv

# Postgres connection (settings.py now reads these; defaults match docker-compose.yaml)
POSTGRES_DB=logisticsdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

> `POSTGRES_HOST=postgres` matches the Postgres service name in `docker-compose.yaml`, so containers can reach it over the compose network. If you ever run Django locally (outside Docker) against a local Postgres install, set `POSTGRES_HOST=localhost` instead.

### 3.4 Run it — Option A: Docker Compose (recommended)

```bash
docker compose build
docker compose up
```

This starts:

- `postgres` — a Postgres container (`logisticsdb` / `postgres` / `postgres`)
- `web` — runs `python manage.py migrate` then `python manage.py runserver 0.0.0.0:8000`, mounts the repo into `/app`, and exposes port `8000`

API will be reachable at `http://localhost:8000/api/v1/`.

### 3.5 Run it — Option B: Local (no Docker)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # requires GDAL/PROJ system libraries installed locally
cd logisticsapi
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3.6 Verify
```bash
curl http://localhost:8000/api/v1/
```
Expect a JSON response with `status: "Logistics Engine Online"`.

---

## 4. API Endpoints

Base path: `/api/v1/`

### `GET /api/v1/`
API root / health check. Returns hyperlinks to the other endpoints.

**Response 200**
```json
{
  "ports": "http://localhost:8000/api/v1/ports",
  "shortest-path": "http://localhost:8000/api/v1/shortest-path/",
  "status": "Logistics Engine Online",
  "version": "v1.0.0"
}
```

### `GET /api/v1/ports`
Returns every node currently in the graph (all airport and seaport names loaded at startup).

**Response 200**
```json
{
  "ports": ["Addis Ababa Bole International Airport", "Changdianhekou", "..."]
}
```

### `POST /api/v1/shortest-path/`
Computes the shortest weighted path (in miles) between two named nodes using Dijkstra's algorithm.

**Request body**
```json
{
  "start_point": "Addis Ababa Bole International Airport",
  "end_point": "Changdianhekou"
}
```

**Response 200**
```json
{
  "start_point": "Addis Ababa Bole International Airport",
  "end_point": "Changdianhekou",
  "distance_miles": 1234,
  "map_polyline": [[lat, lng], [lat, lng], "..."],
  "path_details": [
    {
      "name": "Addis Ababa Bole International Airport",
      "latitude": 8.98,
      "longitude": 38.79,
      "country_code": "ET",
      "category": "air"
    }
  ]
}
```

**Error responses**
- `400` — `{"error": "Start and end points are required."}` if either field is missing.
- `404` — `{"error": "One or both ports not found, or no path exists."}` when a node name doesn't exist in the graph or no path connects the two nodes.
- `400` — serializer validation errors if the computed result fails schema validation.

### `/admin/`
Standard Django admin site (uses `SECRET_KEY`/`DEBUG` from `settings.py`).

---

## 5. Data Model

`api/models.py` defines a `Path` model (not currently used by the routing endpoints, but migrated into the DB):

| field | type |
|---|---|
| `origin` | CharField(100) |
| `destination` | CharField(100) |
| `distance_km` | FloatField |

---

## 6. Running Tests

```bash
cd logisticsapi
python manage.py test
```

`api/tests.py` includes two `APITestCase`s: a successful lookup (`Addis Ababa Bole International Airport` → `Changdianhekou`) and an invalid-port-name case expecting a `404`. These tests depend on your dataset actually containing those node names — swap in names that exist in your own airport/seaport CSVs if they don't match.

---

## Debugging Tips for This Project

**Where to look first, by symptom:**

- **App won't start / graph errors on boot** → check `apps.py`'s `ready()` — it wraps graph construction in a try/except that prints the error but doesn't crash the app, so a broken dataset can silently leave `self.graph = None`, which will then throw `AttributeError` on any request. Check container/console logs for `"Error during graph processing: ..."`.
- **404 on a real-looking port name** → node names are exact strings from the `name` column in your CSVs; check for whitespace, casing, or encoding mismatches. Use `GET /api/v1/ports` to see exactly what's loaded.
- **CSV won't load** → confirm it's semicolon-delimited (`sep=';'` in `graph_setup.py`) and has `name`, `latitude`, `longitude`, `country_code` columns.
- **Env vars not found** → confirm `.env` sits at the repo root and paths in `AIR_DATASET`/`SEA_DATASET` are relative to the repo root, not to `logisticsapi/`.
- **DB connection refused / `could not connect to server`** → confirm the `POSTGRES_*` env vars are set (§3.3) and, if running in Docker, that `POSTGRES_HOST=postgres` (the compose service name) rather than `localhost`. If running Django outside Docker against a local Postgres instance, use `POSTGRES_HOST=localhost` instead.
- **`django.db.utils.OperationalError` / migrations failing** → make sure `psycopg2-binary` (or `psycopg[binary]`) is installed and the `postgres` container is up and healthy before running `migrate`.
- **GeoPandas/pyogrio import errors locally (non-Docker)** → almost always missing system GDAL/PROJ libraries; see the `dockerfile` for the exact apt packages needed.
- **`pip install -r requirements.txt` fails with odd parsing errors** → `requirements.txt` is now plain UTF-8; if this recurs, someone likely re-saved it in an editor with a non-UTF-8 default encoding (see the PowerShell fix for converting it back).