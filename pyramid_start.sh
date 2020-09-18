#!/bin/sh

set -e

/usr/local/bin/python check_celery_running.py

/usr/local/bin/pserve /run/secrets/production.ini
