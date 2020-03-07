import os
import sys
import argparse
import django
from django.core.management import execute_from_command_line
from aiohttp import web
from serverside.django import get_apps


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--makemigrations", default=False, action="store_true", help="Makemigrations")
    parser.add_argument("--migrate", default=False, action="store_true", help="Makemigrations")
    parser.add_argument("--mode", default="dev", type=str, help="Mode of server..")
    args = parser.parse_args()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{args.mode}")
    django.setup()

    from django.conf import settings
    from config.routes import routes

    apps = get_apps(settings.INSTALLED_APPS)

    if args.makemigrations is True:
        print("// Making Migrations")
        execute_from_command_line(["manage.py", "makemigrations"] + apps)
        sys.exit()
    elif args.migrate is True:
        print("// Migrating")
        execute_from_command_line("manage.py migrate".split())
        sys.exit()

    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host="0.0.0.0", port="8080")
