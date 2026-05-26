import os
from dotenv import load_dotenv

from pathlib import Path
root_path = str(Path('.'))
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
image_path = '%s/images/'%os.getenv('S3_URL') if os.getenv('FILE_STORAGE') == 'S3' else "%s/static/images/"%(os.getenv("APP_URL"))

# Central Configuration
SYNC_CENTRAL = os.getenv("SYNC_CENTRAL", "false").lower() == "true"
CENTRAL_API_KEY = os.getenv("CENTRAL_API_KEY", "")
CENTRAL_BASE_URL = os.getenv("CENTRAL_BASE_URL", "")

class Settings:
    PROJECT_NAME        :str  = "InnoTech Backend API"
    POS_PROJECT_NAME    :str  = "InnoTech POS API"
    MOBILE_PROJECT_NAME :str  = "InnoTech Mobile API"
    PROJECT_VERSION     :str  = "1.0.0"
    
    ORIGINS = os.getenv("ALLOWED_HOSTS",'*').split(',')
    
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
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    CRUD_RATE_LIMIT_BACKEND = os.getenv("CRUD_RATE_LIMIT_BACKEND", "memory")
    CRUD_RATE_LIMIT_REDIS_PREFIX = os.getenv("CRUD_RATE_LIMIT_REDIS_PREFIX", "rate:crud")
    
    CYTHON_OUTPUT_DIR = os.getenv("CYTHON_OUTPUT_DIR", "generated")
    VERSION = os.getenv("VERSION", "1.0.0")

    # KeyCloak Config
    KEYCLOAK_ENABLED : str = os.getenv("KEYCLOAK_ENABLED")
    KEYCLOAK_URL     : str = os.getenv("KEYCLOAK_URL")
    REALM            : str = os.getenv("KEYCLOAK_REALM")
    CLIENT_ID        : str = os.getenv("KEYCLOAK_CLIENT_ID")
    CLIENT_SECRET    : str = os.getenv("KEYCLOAK_CLIENT_SECRET")
    KEYCLOAK_ADMIN          : str = os.getenv("KEYCLOAK_ADMIN")
    KEYCLOAK_ADMIN_PASSWORD : str = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
    # Webhook
    SYSTEM_ID      : str = os.getenv("SYSTEM_ID")
    APP_BASE_URL   : str = os.getenv("APP_BASE_URL")
    WEBHOOK_SECRET : str = os.getenv("WEBHOOK_SECRET")
    CRUD_REQUEST_SIGNATURE_SECRET : str = os.getenv("CRUD_REQUEST_SIGNATURE_SECRET", "")

settings = Settings()
