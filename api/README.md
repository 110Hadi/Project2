# MQ-2 readings API

The Pico W sends raw 16-bit ADC samples to this service. The service checks a
shared bearer token and inserts each sample into Neon PostgreSQL.

## Local setup

The Pico W is powered from the laptop USB port and joins the same Wi-Fi network
as the laptop. The Pico posts each raw 16-bit MQ-2 ADC sample to the laptop's
local API, and the API inserts it into Neon. The current Pico URL is
`http://192.168.1.140:8000/api/readings`; update that address in `newMQ2.py`
if the laptop receives a different Wi-Fi IP later.

Run `python -m pip install -r requirements.txt` once, then start the API from
this directory with `python -m uvicorn app:app --host 0.0.0.0 --port 8000`.
Keep the laptop and Pico on the same Wi-Fi network. The Neon table
`mq2_readings` must already exist.

The Wi-Fi, API token, and Neon connection settings are currently written
directly in the source files for this local setup.

## Endpoint

`POST /api/readings`

Header: `Authorization: Bearer <DEVICE_TOKEN>`

JSON body: `{"value": 12345, "device_id": "pico-mq2-1"}`

Successful inserts return HTTP 201 and the inserted row's ID and database
timestamp. `GET /health` is a public service health check.
