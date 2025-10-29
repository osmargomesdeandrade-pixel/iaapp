#!/usr/bin/env python
"""Minimal manage.py for django template (keeps imports at top for linters)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    try:
        # Import here to keep manage.py lightweight when Django isn't installed
        from django.core.management import execute_from_command_line
    except ImportError:
        # This template does not require Django to be installed in the generator.
        print("Django is not installed. This is a template only.")
        return

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
