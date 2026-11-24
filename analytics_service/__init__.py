import sys
import os

pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "analytics-service"))
__path__.append(pkg_dir)

from analytics_service.app.main import create_app, app
__all__ = ["create_app", "app"]
