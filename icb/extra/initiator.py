import os
import typer
import time


def run(output_dir: str = ".", force: bool = False):
    abs_dir = os.path.abspath(output_dir)
    typer.echo(f"Writing to: {abs_dir}\n")
    folders = ["static", "log"]
    for folder in folders:
        folder_path = os.path.join(abs_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        typer.echo(f"  --> {folder_path}")
    files = {
        ".env":      _env_template(),
        "main.py":   _main_template(),
        "config.py": _config_template(),
    }

    with typer.progressbar(files.items(), label="Generating files", length=len(files)) as progress:
        for filename, content in progress:
            time.sleep(0.3)  # optional: makes it feel less instant
            path = os.path.join(abs_dir, filename)
            if os.path.exists(path) and not force:
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    typer.echo("\n[done] Files created:")
    for filename in files:
        path = os.path.join(abs_dir, filename)
        if os.path.exists(path):
            typer.echo(f"  --> {path}")

    typer.echo("\nNext steps:")
    typer.echo("  1. Edit .env with your real values")
    typer.echo("  2. Run:  python main.py")


# ── Templates ─────────────────────────────────────────────────────────────────
# Edit these freely — whatever you write here is what gets generated.

def _env_template() -> str:
    return """\
DB_USER=postgres
DB_PASSWORD=3108
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=test_db
# DB_NAME=test_db_2
APP_URL=http://127.0.0.1:8000
FRONTEND_URL=http://localhost:4000


PLASGATE_PRIVATE_KEY=''
PLASGATE_SECRET=''
PLASGATE_SENDER=''


PLASGATE_USER=''
PLASGATE_PASS=''


EXT_TOKEN_EXPIRE_MINUTES=10080
FIXED_OTP='YES'
ENABLE_LOG_REQUEST='YES'


S3_ACCESS_KEY=''
S3_SECRET_KEY=''
S3_BUCKET=''
FILE_STORAGE=''
S3_URL=''


# REDIS_URL = ""
ENVIROMENT=


PG_DUMP="/Library/PostgreSQL/17/pgAdmin 4.app/Contents/SharedSupport/pg_dump"
PG_RESTORE="/Library/PostgreSQL/17/pgAdmin 4.app/Contents/SharedSupport/pg_restore"


# AES ENCRYPTION
AES_SECRET_KEY=
ASE_ENCRYPTION=nz8KdvADy7pe8Mn7xBGJbZdEFxK7GiSCSY9aP3BWxE

# Keycloak configuration
KEYCLOAK_ENABLED = false
KEYCLOAK_URL    = http://localhost:8080
KEYCLOAK_REALM  = MyRealm
KEYCLOAK_CLIENT_ID      = my-fastapi-app
KEYCLOAK_CLIENT_SECRET  = vxmpYUkfyUgnsTvjpiG0VPHwMcjDgjaH

KEYCLOAK_ADMIN          = admin
KEYCLOAK_ADMIN_PASSWORD = admin

# OTP and Link
CODE_TTL_MINUTES = 10
SMTP_HOST        = smtp.gmail.com
SMTP_PORT        = 587
SMTP_USER        = metalslug4213@gmail.com
SMTP_PASSWORD    = hlvipudacpismwrf

# Webhook
SYSTEM_ID        = SALE
WEBHOOK_SECRET   = testing
APP_BASE_URL     = http://host.docker.internal:8000
"""


def _config_template() -> str:
    return """\
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

settings = Settings()
"""


def _main_template() -> str:
    return """\
#from mount_cython_path import *
from fastapi import FastAPI, Body, Request, Response
from icb.sample.config import settings
from fastapi.responses import HTMLResponse, JSONResponse

from typing import Annotated, Optional
from fastapi import Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, uuid, time

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from collections import defaultdict
# from icb.core import *

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION, 
    swagger_ui_parameters={"docExpansion": "none", "filter": True, "tagsSorter": "alpha",},
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
@app.get("/custom/docs", include_in_schema=False)
async def custom_docs():
    if os.path.exists("templates/docs.html") :
        with open("templates/docs.html", encoding="utf-8") as f:  
            return HTMLResponse(f.read())
    pass    

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], # allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    app.state.request_id = request_id

    # if check_app_is_offline(request) or check_system_is_offline(request):
    #     return offline_response()

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    if os.getenv('ENABLE_LOG_REQUEST', 'NO') == 'YES' and not request.url.path.startswith('/static'):  
        content_type = response.headers.get("content-type", "")
        # if "text" in content_type or "json" in content_type or "html" in content_type:
        #     response_body = [chunk async for chunk in response.body_iterator]
        #     response.body_iterator = iterate_in_threadpool(iter(response_body))

    return response

def cache_key_builder(func, namespace: Optional[str] = "", request: Request = None, response: Response = None, *args, **kwargs):
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return cache_key

@app.on_event("startup")
def startup():
    # https://pypi.org/project/fastapi-cache2/ 
    # https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04
    # int cache with redis
    redis = aioredis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379"), encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix=f"fastapi-{settings.POSTGRES_DB}",key_builder=cache_key_builder)

@app.get('/test-cache')
@cache(expire=30)
async def test_cache_page():
    print('in route catche')
    return JSONResponse({"success": True, "message": "this data should only be cached temporarily"}, status_code=200)

@app.get('/', response_class=HTMLResponse)
async def home_page():
    html_path = "templates/home.html"
    static_path = "static"
    # for route in app.routes:
    #     print(route.path)
    if os.path.exists(html_path) and os.path.exists(static_path):
        with open(html_path, encoding="utf-8") as f:
            return HTMLResponse(f.read())
    html = '''
        <center>
        <h1>Welcome To InnoTech</h1>
        <p><a href="/docs">Visit Backend API Document</a></p>
        <p><a href="/api/v1/pos/docs">Visit POS API Document</a></p>
        <p><a href="/api/v1/m/docs">Visit Mobile API Document</a></p>
        </center>        
    '''
    return HTMLResponse(content=html, status_code=200)

from icb.api.user.views import *
from icb.api.store.views import *
from icb.api.company.views import *
from icb.api.workflow.views import *
from icb.api.role.views import *
from icb.api.api_token.views import *
from icb.api.module.views import *
from icb.api.branch.views import *
# from modules.register import *
if settings.KEYCLOAK_ENABLED == "true":
    from icb.core.webhook import *
@app.on_event("startup")
def check_duplicate_routes():
    route_map = defaultdict(list)

    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                key = (method, route.path)
                route_map[key].append(route.name)

    duplicates = {k: v for k, v in route_map.items() if len(v) > 1}
    
    if duplicates:
        print("🚨 Duplicate routes found:")
        for (method, path), handlers in duplicates.items():
            print(f"  {method} {path} -> {handlers}")
    # else:
    #     print("✅ No duplicate routes found.")

"""