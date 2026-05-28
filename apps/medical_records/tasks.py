from celery import shared_task


@shared_task
def retry_pending_supply_sync():
    # Punto de integración para reintentos contra Backend 2.
    return 'queued'
