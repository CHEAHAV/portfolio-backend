import os
from dotenv import load_dotenv
from pathlib import Path

root_path = str(Path('.'))
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
image_path = '%s/images/'%os.getenv('S3_URL') if os.getenv('FILE_STORAGE') == 'S3' else "%s/static/images/"%(os.getenv("APP_URL"))

def _env_list(*names, default=''):
    values = []
    for name in names:
        raw_value = os.getenv(name, '')
        values.extend(value.strip() for value in raw_value.split(','))
    values = [value for value in values if value]
    if values:
        return list(dict.fromkeys(values))
    return [default] if default else []

# Central Configuration
SYNC_CENTRAL = os.getenv("SYNC_CENTRAL", "false").lower() == "true"
CENTRAL_API_KEY = os.getenv("CENTRAL_API_KEY", "")
CENTRAL_BASE_URL = os.getenv("CENTRAL_BASE_URL", "")

class Settings:
    PROJECT_NAME        :str  = "Portfolio Backend API"
    POS_PROJECT_NAME    :str  = "Portfolio POS API"
    MOBILE_PROJECT_NAME :str  = "Portfolio Mobile API"
    PROJECT_VERSION     :str  = "1.0.0"
    
    APP_URL = os.getenv("APP_URL", "").strip()
    FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip()
    ORIGINS = _env_list("CORS_ORIGINS", "ALLOWED_HOSTS", "FRONTEND_URL", default="*")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "469efa472104afa04213fec4aca08038f37babd0f1b9f5126daa58dd4263f745")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("TOKEN_EXPIRE_MINUTES", 60*24*7)

    FIREBASE_CREDENTIAL_PATH = os.getenv("FIREBASE_CREDENTIAL_PATH", "")

    POSTGRES_USER : str = os.getenv("DB_USER")
    POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
    POSTGRES_SERVER : str = os.getenv("DB_SERVER","localhost")
    POSTGRES_PORT : str = os.getenv("DB_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str = os.getenv("DB_NAME","tdd")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    MAX_DAY_PER_MONTH = 1.5
    MISSED_AFTER = 2
    
    # AES Encryption
    AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "469efa472104afa04213fec4aca08038f37babd0f1b9f5126daa58dd4263f745")

    # Central Configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    
    CYTHON_OUTPUT_DIR = os.getenv("CYTHON_OUTPUT_DIR", "generated")
    VERSION = os.getenv("VERSION", "1.0.0")

    KEYCLOAK_ENABLED = os.getenv("KEYCLOAK_ENABLED", "false").strip().lower()
    KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "").strip()
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "").strip()
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "").strip()
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "").strip()
    KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN", "").strip()
    KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "").strip()

settings = Settings()
