import csv
import os
import time
from datetime import datetime
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from .celery_app import celery_app
from .database import SessionLocal
from . import models, crud


@celery_app.task(name="app.tasks.import_csv_job")
def import_csv_job(job_id: str, file_path: str):
    db: Session = SessionLocal()
    try:
        job = crud.get_import_job(db, UUID(job_id))
        if not job:
            return

        job.status = "parsing"
        job.started_at = datetime.utcnow()
        db.commit()

        # First pass: count rows (excluding header)
        total_rows = 0
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for _ in reader:
                total_rows += 1

        job.total_rows = total_rows
        job.status = "importing"
        job.processed_rows = 0
        db.commit()

        # Second pass: actual import
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            batch_size = 500
            processed = 0

            for row in reader:
                sku = row.get("sku") or row.get("SKU") or row.get("Sku")
                if not sku:
                    continue

                name = row.get("name") or row.get("Name")
                description = row.get("description") or row.get("Description")
                price_raw = row.get("price") or row.get("Price")

                try:
                    price = float(price_raw) if price_raw else None
                except ValueError:
                    price = None

                sku_norm = crud.normalize_sku(sku)
                existing = (
                    db.query(models.Product)
                    .filter(models.Product.sku_normalized == sku_norm)
                    .first()
                )

                if existing:
                    # Overwrite fields
                    existing.sku = sku
                    existing.name = name
                    existing.description = description
                    existing.price = price
                else:
                    product = models.Product(
                        sku=sku,
                        sku_normalized=sku_norm,
                        name=name,
                        description=description,
                        price=price,
                        active=True,
                    )
                    db.add(product)

                processed += 1
                job.processed_rows = processed
                if processed % batch_size == 0:
                    db.commit()

            db.commit()

        job.status = "completed"
        job.finished_at = datetime.utcnow()
        db.commit()

        # Trigger webhooks for event "product.import.completed"
        trigger_webhooks.delay("product.import.completed")

    except Exception as e:
        job = crud.get_import_job(db, UUID(job_id))
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
        # Optionally remove temp file
        try:
            os.remove(file_path)
        except OSError:
            pass


@celery_app.task(name="app.tasks.test_webhook")
def test_webhook(webhook_id: int):
    db: Session = SessionLocal()
    try:
        webhook = crud.get_webhook(db, webhook_id)
        if not webhook:
            return

        start = time.time()
        try:
            response = requests.post(
                webhook.url,
                json={"test": True, "event_type": webhook.event_type},
                timeout=5,
            )
            code = response.status_code
        except Exception:
            code = None
        elapsed_ms = (time.time() - start) * 1000

        webhook.last_response_code = code
        webhook.last_response_time_ms = elapsed_ms
        db.commit()
    finally:
        db.close()


@celery_app.task(name="app.tasks.trigger_webhooks")
def trigger_webhooks(event_type: str):
    db: Session = SessionLocal()
    try:
        webhooks = (
            db.query(models.Webhook)
            .filter(models.Webhook.event_type == event_type,
                    models.Webhook.enabled == True)
            .all()
        )
        for wh in webhooks:
            test_webhook.delay(wh.id)
    finally:
        db.close()
