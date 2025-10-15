# core/config_loader.py
import os
from dotenv import load_dotenv
from threading import Lock

load_dotenv()

class ConfigLoader:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigLoader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # avoid double init
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        # Load environment-backed settings
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-dev")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", None)
        self.AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", None)
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
