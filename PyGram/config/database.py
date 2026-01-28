# config/database.py
import os

DATABASES = {
    'default': os.getenv('DB_CONNECTION', 'mysql'),
    'connections': {
        'mysql': {
            'driver': 'mysql',
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_DATABASE', 'YL'),
            'username': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
            'collation': os.getenv('DB_COLLATION', 'utf8mb4_unicode_ci'),
        }
    }
}