from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Products ----------
def normalize_sku(sku: str) -> str:
    return sku.strip().lower()


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[models.Product]:
    sku_norm = normalize_sku(sku)
    return (
        db.query(models.Product)
        .filter(models.Product.sku_normalized == sku_norm)
        .first()
    )


def list_products(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
) -> Tuple[List[models.Product], int]:
    query = db.query(models.Product)

    if sku:
        sku_like = f"%{sku}%"
        query = query.filter(models.Product.sku.ilike(sku_like))

    if name:
        name_like = f"%{name}%"
        query = query.filter(models.Product.name.ilike(name_like))

    if description:
        desc_like = f"%{description}%"
        query = query.filter(models.Product.description.ilike(desc_like))

    if active is not None:
        query = query.filter(models.Product.active == active)

    total = query.count()

    items = (
        query.order_by(models.Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def create_product(db: Session, data: schemas.ProductCreate) -> models.Product:
    if get_product_by_sku(db, data.sku):
        raise ValueError("SKU already exists (case-insensitive).")

    sku_norm = normalize_sku(data.sku)
    product = models.Product(
        sku=data.sku,
        sku_normalized=sku_norm,
        name=data.name,
        description=data.description,
        price=data.price,
        active=data.active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: models.Product, data: schemas.ProductUpdate) -> models.Product:
    if data.sku is not None:
        new_norm = normalize_sku(data.sku)
        existing = (
            db.query(models.Product)
            .filter(models.Product.sku_normalized == new_norm, models.Product.id != product.id)
            .first()
        )
        if existing:
            raise ValueError("SKU already exists (case-insensitive).")
        product.sku = data.sku
        product.sku_normalized = new_norm

    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.active is not None:
        product.active = data.active

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: models.Product) -> None:
    db.delete(product)
    db.commit()


def delete_all_products(db: Session) -> int:
    count = db.query(models.Product).delete()
    db.commit()
    return count


# ---------- Import Jobs ----------
def create_import_job(db: Session, filename: str) -> models.ImportJob:
    job = models.ImportJob(filename=filename, status="pending", processed_rows=0)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_import_job(db: Session, job_id: UUID) -> Optional[models.ImportJob]:
    return db.query(models.ImportJob).filter(models.ImportJob.id == job_id).first()


# ---------- Webhooks ----------
def list_webhooks(db: Session) -> List[models.Webhook]:
    return db.query(models.Webhook).order_by(models.Webhook.id.desc()).all()


def create_webhook(db: Session, data: schemas.WebhookCreate) -> models.Webhook:
    webhook = models.Webhook(
        url=str(data.url),
        event_type=data.event_type,
        enabled=data.enabled,
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


def get_webhook(db: Session, webhook_id: int) -> Optional[models.Webhook]:
    return db.query(models.Webhook).filter(models.Webhook.id == webhook_id).first()


def update_webhook(
    db: Session, webhook: models.Webhook, data: schemas.WebhookUpdate
) -> models.Webhook:
    if data.url is not None:
        webhook.url = str(data.url)
    if data.event_type is not None:
        webhook.event_type = data.event_type
    if data.enabled is not None:
        webhook.enabled = data.enabled

    db.commit()
    db.refresh(webhook)
    return webhook


def delete_webhook(db: Session, webhook: models.Webhook) -> None:
    db.delete(webhook)
    db.commit()
