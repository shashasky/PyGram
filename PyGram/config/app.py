import os

APP_NAME = os.getenv("APP_NAME", "PyGram")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Shanghai")