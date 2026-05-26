# gunicorn_conf.py
from multiprocessing import cpu_count

bind = "127.0.0.1:5055"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/var/www/apibackend/access_log'
errorlog =  '/var/www/apibackend/error_log'