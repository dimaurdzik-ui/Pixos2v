import asyncio
from apps.api.app.main import app

def check():
    for route in app.routes:
        print(getattr(route, "methods", None), getattr(route, "path", route.name))

check()
