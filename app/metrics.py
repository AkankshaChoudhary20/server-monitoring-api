import psutil
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

CPU_WARNING_THRESHOLD = 80
MEMORY_WARNING_THRESHOLD = 80
DISK_CRITICAL_THRESHOLD = 90

CPU_GAUGE = Gauge("server_cpu_usage_percent", "CPU usage percent")
MEMORY_GAUGE = Gauge("server_memory_usage_percent", "Memory usage percent")
DISK_GAUGE = Gauge("server_disk_usage_percent", "Disk usage percent")


def get_cpu_metrics() -> dict:
    return {"usage_percent": psutil.cpu_percent(interval=0.5)}


def get_memory_metrics() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "usage_percent": mem.percent,
    }


def get_disk_metrics() -> dict:
    disk = psutil.disk_usage("/")
    return {
        "total": disk.total,
        "used": disk.used,
        "usage_percent": disk.percent,
    }


def get_all_metrics() -> dict:
    return {
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
    }


def get_status_report() -> dict:
    cpu = get_cpu_metrics()["usage_percent"]
    memory = get_memory_metrics()["usage_percent"]
    disk = get_disk_metrics()["usage_percent"]

    alerts = []
    status = "OK"

    if cpu > CPU_WARNING_THRESHOLD:
        alerts.append(f"CPU usage is above {CPU_WARNING_THRESHOLD}%")
        status = "WARNING"

    if memory > MEMORY_WARNING_THRESHOLD:
        alerts.append(f"Memory usage is above {MEMORY_WARNING_THRESHOLD}%")
        status = "WARNING"

    if disk > DISK_CRITICAL_THRESHOLD:
        alerts.append(f"Disk usage is above {DISK_CRITICAL_THRESHOLD}%")
        status = "CRITICAL"

    return {
        "status": status,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "alerts": alerts,
    }


def get_prometheus_metrics() -> bytes:
    CPU_GAUGE.set(get_cpu_metrics()["usage_percent"])
    MEMORY_GAUGE.set(get_memory_metrics()["usage_percent"])
    DISK_GAUGE.set(get_disk_metrics()["usage_percent"])
    return generate_latest()
