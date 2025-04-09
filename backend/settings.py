import os

SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret")
DEBUG = os.environ.get("DEBUG", "False") == "True"
CLIENT_URL = os.environ.get("CLIENT_URL", "http://localhost:5173")