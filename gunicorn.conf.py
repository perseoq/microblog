import os

bind = f"0.0.0.0:{os.getenv('PORT', '10222')}"
workers = int(os.getenv('WEB_CONCURRENCY', '3'))
threads = int(os.getenv('GUNICORN_THREADS', '2'))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
accesslog = '-'
errorlog = '-'
