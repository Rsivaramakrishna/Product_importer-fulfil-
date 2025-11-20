# Product Importer (FastAPI + Celery + PostgreSQL)

A simple web application that allows users to:

- Upload a large CSV file (up to 500,000 products)
- Track real-time upload & import progress
- View, filter, create, edit, delete products
- Bulk delete all products
- Manage webhooks and test them
- All operations are done through a simple HTML/JS UI

---

## 🚀 Tech Stack

- **FastAPI** – backend web framework  
- **Celery** – background worker for long tasks (CSV import, webhook tests)  
- **Redis** – Celery broker  
- **PostgreSQL** – main database  
- **SQLAlchemy** – ORM  
- **HTML + JavaScript** – simple UI  
- **Uvicorn** – server  

---

## 📁 Features Overview

### ✅ CSV Upload (up to 500k rows)
- Upload CSV file through UI
- Import happens in background using Celery
- Real-time progress (status, percentage, processed rows)
- Overwrites duplicate products based on **case-insensitive SKU**

### ✅ Product Management UI
- View products (paginated)
- Filter by SKU, name, description, active status
- Add product
- Edit product
- Delete product

### ✅ Bulk Delete
- Delete all products from DB
- Confirmation popup to avoid accidental delete

### ✅ Webhooks
- Add / edit / delete webhook URLs
- Supported event: `product.import.completed`
- Test webhook and see last response time & HTTP code

---

## 🛠️ Requirements

Install these before running the project:

- Python 3.9+
- PostgreSQL
- Redis
- pip

---

## 🔧 Installation & Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd product_importer
