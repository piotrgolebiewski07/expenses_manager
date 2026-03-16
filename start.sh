#!/bin/bash

echo "Creating tables..."
python - <<'PY'
from app.db.session import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
PY

echo "Seeding database..."
python -m scripts.seed_data

echo "Starting API..."
uvicorn app.main:app --host 0.0.0.0 --port 8000