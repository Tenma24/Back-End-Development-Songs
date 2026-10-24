# Back-End-Development-Songs

Flask REST service backed by real MongoDB. Startup seeds missing records without deleting existing data.

Start MongoDB, then set MONGODB_SERVICE=127.0.0.1:27017.
PowerShell: `$env:MONGODB_SERVICE='127.0.0.1:27017'`.

```sh
python -m pip install -r requirements.txt
python -m pytest -v
waitress-serve --listen=127.0.0.1:5000 backend:app
```

Optional environment: MONGODB_URI, MONGODB_DATABASE (default capstone_songs), MONGODB_USERNAME, MONGODB_PASSWORD.
Endpoints: GET /health, GET /count, GET/POST /song, GET/PUT/DELETE /song/<id>.
Duplicate POST returns 302 and changed PUT returns 201, matching the IBM lab contract.
CRUD tests create and remove only their own randomly numbered test record.

## Source

Based on the [official IBM Skills Network starter](https://github.com/ibm-developer-skills-network/hvlga-Back-End-Development-Songs). Original starter history and course fixtures are retained.
