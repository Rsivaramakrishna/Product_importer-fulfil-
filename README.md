# Product Importer (FastAPI + Celery + Postgres)

## Quick Start

1. Create and start Postgres and Redis (for example using Docker):

```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=products_db -p 5432:5432 -d postgres
docker run --name redis -p 6379:6379 -d redis
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set env variables (or use a `.env` file):

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/products_db
export REDIS_URL=redis://localhost:6379/0
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

5. Start Celery worker (in another terminal):

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

6. Open the UI in your browser:

```
http://localhost:8000/
```

- Use **Import** tab to upload a CSV with columns: `sku,name,description,price`.
- Use **Products** tab to view/filter/edit products.
- Use **Bulk Delete** tab to delete all products.
- Use **Webhooks** tab to configure webhooks.
