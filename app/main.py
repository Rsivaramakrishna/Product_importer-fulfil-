from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import os
import shutil

from .database import Base, engine, get_db
from . import schemas, crud
from .tasks import import_csv_job, test_webhook

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Importer")

# Static UI
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def root():
    # serve the frontend
    return FileResponse("static/index.html")


# --------- IMPORT API ---------
@app.post("/api/imports/", response_model=schemas.ImportJobOut)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # save temp file
    temp_dir = "tmp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = crud.create_import_job(db, filename=file.filename)
    import_csv_job.delay(str(job.id), temp_path)
    return job


@app.get("/api/imports/{job_id}", response_model=schemas.ImportJobOut)
def get_import(job_id: UUID, db: Session = Depends(get_db)):
    job = crud.get_import_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return job


# --------- PRODUCT CRUD ---------
@app.get("/api/products", response_model=schemas.PaginatedProducts)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    items, total = crud.list_products(
        db, page=page, page_size=page_size,
        sku=sku, name=name, description=description,
        active=active,
    )
    return schemas.PaginatedProducts(
        items=items, page=page, page_size=page_size, total=total
    )


@app.post("/api/products", response_model=schemas.ProductOut)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        product = crud.create_product(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return product


@app.get("/api/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/products/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product = crud.update_product(db, product, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.delete_product(db, product)
    return {"deleted": True}


@app.delete("/api/products")
def delete_all_products(db: Session = Depends(get_db)):
    deleted_count = crud.delete_all_products(db)
    return {"deleted_count": deleted_count}


# --------- WEBHOOKS ---------
@app.get("/api/webhooks", response_model=List[schemas.WebhookOut])
def list_webhooks(db: Session = Depends(get_db)):
    return crud.list_webhooks(db)


@app.post("/api/webhooks", response_model=schemas.WebhookOut)
def create_webhook(data: schemas.WebhookCreate, db: Session = Depends(get_db)):
    return crud.create_webhook(db, data)


@app.put("/api/webhooks/{webhook_id}", response_model=schemas.WebhookOut)
def update_webhook(
    webhook_id: int, data: schemas.WebhookUpdate, db: Session = Depends(get_db)
):
    webhook = crud.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return crud.update_webhook(db, webhook, data)


@app.delete("/api/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    webhook = crud.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    crud.delete_webhook(db, webhook)
    return {"deleted": True}


@app.post("/api/webhooks/{webhook_id}/test")
def test_webhook_endpoint(webhook_id: int, db: Session = Depends(get_db)):
    webhook = crud.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    test_webhook.delay(webhook_id)
    return {"status": "queued"}
