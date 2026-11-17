# MQ-2 readings API

The Pico W sends raw 16-bit ADC samples to this service. The service checks a
shared bearer token and inserts each sample into Neon PostgreSQL.

## Configure and run

Replace the marked sample `DATABASE_URL` and `DEVICE_TOKEN` values at the top
of `app.py`. Use the pooled connection string from Neon. Use the exact same
token in `send_reading.py`. Run the SQL in `schema.sql` once in the Neon SQL
Editor. Then install `requirements.txt` and run
`uvicorn app:app --host 0.0.0.0 --port 8000` from this directory.

For deployment, use the service's HTTPS URL on the Pico. Replace all marked
sample settings before deployment; the example token is public and must not be
used as a real security token.

## Endpoint

`POST /api/readings`

Header: `Authorization: Bearer <DEVICE_TOKEN>`

JSON body: `{"value": 12345, "device_id": "pico-mq2-1"}`

Successful inserts return HTTP 201 and the inserted row's ID and database
timestamp. `GET /health` is a public service health check.
