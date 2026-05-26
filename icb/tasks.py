import httpx
import time
import icb.celeryconfig as celeryconfig
from celery import Celery
from icb.lib.logger_sync import write_sync_log

celery_app = Celery("tasks")
celery_app.config_from_object(celeryconfig)

@celery_app.task(bind=True, max_retries=3)
def push_sync_task(
    self, endpoint: str, data: dict, api_key: str, base_url: str,
    *, module: str, tables: dict, record_count: int
):
    start_time = time.time()
    task_id = self.request.id
    attempt = self.request.retries + 1

    try:
        url = f"{base_url}{endpoint}"
        headers = {"X-SCF-API-KEY": api_key}

        response = httpx.post(url, json=data, headers=headers)
        response.raise_for_status()

        duration = round(time.time() - start_time, 3)
        write_sync_log(
            module=module,
            tables=tables,
            record_count=record_count,
            status="success",
            attempt=attempt,
            task_id=task_id,
            duration=duration
        )
    except Exception as e:
        duration = round(time.time() - start_time, 3)
        if self.request.retries >= self.max_retries:
            # Final retry failed
            write_sync_log(
                module=module,
                tables=tables,
                record_count=record_count,
                status="failed",
                error=str(e),
                attempt=self.request.retries,
                task_id=task_id,
                duration=duration
            )
        else:
            # Schedule another retry
            raise self.retry(exc=e, countdown=5)