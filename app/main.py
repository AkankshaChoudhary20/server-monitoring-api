import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.metrics import (
    get_all_metrics,
    get_cpu_metrics,
    get_disk_metrics,
    get_memory_metrics,
    get_prometheus_metrics,
    get_status_report,
)
from app.models import MetricRecord


def init_db(retries: int = 10, delay: float = 1.5) -> None:
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == retries:
                raise
            time.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Server Monitoring API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    report = get_status_report()

    record = MetricRecord(
        cpu_usage=report["cpu"],
        memory_usage=report["memory"],
        disk_usage=report["disk"],
        status=report["status"],
    )
    db.add(record)
    db.commit()

    return report


@app.get("/metrics/cpu")
def metrics_cpu():
    return {"cpu": get_cpu_metrics()}


@app.get("/metrics/memory")
def metrics_memory():
    return {"memory": get_memory_metrics()}


@app.get("/metrics/disk")
def metrics_disk():
    return {"disk": get_disk_metrics()}


@app.get("/metrics/raw")
def metrics_raw():
    return get_all_metrics()


@app.get("/metrics/prometheus")
def metrics_prometheus():
    return Response(get_prometheus_metrics(), media_type=CONTENT_TYPE_LATEST)


@app.get("/metrics/history")
def metrics_history(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(MetricRecord).order_by(MetricRecord.timestamp.desc()).limit(limit)
    ).all()

    return [
        {
            "timestamp": row.timestamp.isoformat(),
            "cpu": row.cpu_usage,
            "memory": row.memory_usage,
            "disk": row.disk_usage,
            "status": row.status,
        }
        for row in reversed(rows)
    ]
