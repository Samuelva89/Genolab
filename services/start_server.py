#!/usr/bin/env python3
"""
Script de inicio para la aplicación FastAPI en Render.
Este script cambia al directorio correcto y ejecuta la aplicación con gunicorn.
"""
import os
import sys
from app.main import app
import uvicorn
from gunicorn.app.base import Application
from gunicorn.six import iteritems


class StandaloneApplication(Application):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    options = {
        'bind': f'0.0.0.0:{port}',
        'workers': 4,
        'worker_class': 'uvicorn.workers.UvicornWorker',
        'timeout': 120,
        'max_requests': 1000,
        'max_requests_jitter': 100
    }

    # Ejecutar la aplicación con gunicorn
    StandaloneApplication(app, options).run()