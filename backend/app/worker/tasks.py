from app.worker.celery_app import celery_app


@celery_app.task
def example_task(data: dict) -> dict:
    """Example background task. Replace with actual logic during hackathon."""
    return {"status": "completed", "input": data}
