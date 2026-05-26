#from mount_cython_path import *
from fastapi import FastAPI, Body, Request, Response
from config import settings
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
from modules.register import *
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
