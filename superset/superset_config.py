import os

SQLALCHEMY_DATABASE_URI = (
    "postgresql+psycopg2://superset_user:superset_password@superset-db:5432/superset_db"
)

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "superset-dev-secret-key")
