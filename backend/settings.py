from environs import env

SECRET_KEY = env.str('FLASK_SECRET_KEY', default='default')
DEBUG = env.bool('FLASK_DEBUG', default=False)
ALLOWED_HOSTS = env.list('FLASK_ALLOWED_HOSTS', default=['http://localhost:5173'])