import psycopg
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


# TODO: Replace these sample values before deploying the API.
DATABASE_URL = "postgresql://neondb_owner:npg_cpNXR0EOgD4j@ep-misty-meadow-bev3ppdk-pooler.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
DEVICE_TOKEN = "8nmWa9S8z62d3Ts3RdDB68MNfjCIxWt8mTcBFCatjtw"

app = FastAPI(title="MQ-2 readings API", version="1.0.0")


class Reading(BaseModel):
    value: int = Field(ge=0, le=65535)
    device_id: str = Field(min_length=1, max_length=64)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/readings", status_code=201)
def create_reading(reading: Reading, authorization: str | None = Header(default=None)):
    if "REPLACE_WITH_" in DATABASE_URL or "REPLACE_WITH_" in DEVICE_TOKEN:
        raise HTTPException(status_code=503, detail="API is not configured")

    if authorization != f"Bearer {DEVICE_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=10) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO mq2_readings (value, device_id) VALUES (%s, %s) RETURNING id, recorded_at",
                    (reading.value, reading.device_id),
                )
                row_id, recorded_at = cursor.fetchone()
    except psycopg.Error as exc:
        # Keep credentials and database details out of the public response.
        print(f"Database insert failed:  {type(exc).__name__}")
        raise HTTPException(status_code=503, detail="Database insert failed") from exc

    return {"id": row_id, "value": reading.value, "device_id": reading.device_id,
            "recorded_at": recorded_at.isoformat()}
