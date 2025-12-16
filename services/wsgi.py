"""
WSGI entry point for the Genolab application.
This file provides a WSGI interface for deployment platforms like Render.
"""
import os
import sys

# Add the services directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

# This creates the WSGI callable that Render expects
application = app

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)