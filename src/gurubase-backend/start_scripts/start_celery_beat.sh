#!/bin/bash

set -o errexit
set -o nounset

cd backend && exec celery --app backend beat --pidfile= --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=INFO
