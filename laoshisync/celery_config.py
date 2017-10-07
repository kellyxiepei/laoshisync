# -*- coding: utf-8 -*-
#
#      File: config.py
#   Project: laoshisync
#    Author: Xie Wangyi
#
#   Copyright (c) 2017 Laoshishuo. All rights reserved.

# CELERY
import os

from celery.schedules import crontab

BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_ALWAYS_EAGER = False  # True会把任务变成同步任务，方便pdb
CELERYD_REDIRECT_STDOUTS_LEVEL = 'INFO'
CELERYD_CONCURRENCY = 4
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_DEFAULT_QUEUE = 'laoshisync'

CELERY_INCLUDE = ['tasks']

CELERYBEAT_SCHEDULE = {
    'crawl_momentum': {
        'task': 'laoshisync.crawl_momentum',
        'schedule': crontab(minute=0)
    },
    'crawl_momentum_quote': {
        'task': 'laoshisync.crawl_momentum_quote',
        'schedule': crontab(minute=0)
    },
    'crawl_bing_wallpaper': {
        'task': 'laoshisync.crawl_bing_wallpaper',
        'schedule': crontab(minute=0)
    },
}

WORKING_DIR = os.path.dirname(__file__)
