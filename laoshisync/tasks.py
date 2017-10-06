# -*- coding: utf-8 -*-
#
#      File: config.py
#   Project: laoshisync
#    Author: Xie Wangyi
#
#   Copyright (c) 2017 Laoshishuo. All rights reserved.
import datetime
import os

import requests
from celery.utils.log import get_task_logger

from celery_app import celery as celeryapp
from celery_config import WORKING_DIR

logger = get_task_logger(__name__)


@celeryapp.task(
    bind=True,
    default_retry_delay=10,
    name='laoshisync.hello_world')
def hello_world(self):
    logger.info('hello world!')
    return True


KEY = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2d" \
      "1aWQiOiJlZTBmZWUyMS04ODJhLTQ0MTUtYjY1ZS04NGQyNzFkZmJkOG" \
      "MiLCJpc3MiOiJsb2dpbi1hcGktdjEiLCJleHAiOjE1MzEzODgwMjIsI" \
      "m5iZiI6MTQ5OTg1MjAyMn0.bLUcZ51QORR7Nz40Fx6vY3i1T8NI7lCo" \
      "WB47yLM6WpE"


@celeryapp.task(
    bind=True,
    default_retry_delay=10,
    name='laoshisync.crawl_momentum')
def crawl_momentum(self):
    history_list = json.loads(
        requests.get('https://api.momentumdash.com/backgrounds/history',
                     headers=dict(authorization=KEY)).content)

    for b in history_list['history']:
        file_name = u'{} - momentum - {} - {}.jpg'.format(b['display_date'],
                                                          b['title'].replace(
                                                              '/', '-'),
                                                          b['source'].replace(
                                                              '/', '-'))
        full_file_name = os.path.join(unicode(WORKING_DIR),
                                      u'laoshisync_inbox',
                                      file_name)
        if os.path.isfile(full_file_name):
            logger.info(file_name + u' already exsits.')
            continue
        url = b['preview_url']
        open(full_file_name, "wb").close()  # create the file as mutex signal
        logger.info(u'Downloading "{}"'.format(file_name))
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(full_file_name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

    logger.info('crawl_momentum Finished!')
    return True


@celeryapp.task(
    bind=True,
    default_retry_delay=10,
    name='laoshisync.crawl_momentum_quote')
def crawl_momentum_quote(self):
    today = datetime.date.today()

    for i in range(30):
        date = (today + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
        file_name = u'{} - momentum_quote.txt'.format(date)

        full_file_name = os.path.join(unicode(WORKING_DIR),
                                      u'laoshisync_inbox',
                                      file_name)
        if os.path.isfile(full_file_name):
            logger.info(file_name + u' already exsits.')
            continue
        open(full_file_name, "wb").close()  # create the file as mutex signal
        logger.info(u'Downloading "{}"'.format(file_name))
        r = requests.get(
            'https://api.momentumdash.com/feed/bulk?'
            'syncTypes=quote&localDate={}'.format(date),
            headers=dict(authorization=KEY))
        if r.status_code == 200:
            res_json = r.json()['quotes'][0]
            with open(full_file_name, 'w') as f:
                f.write(u'{} \r\n -- By {}'.format(res_json['body'],
                                                   res_json['source']).encode(
                    'utf-8'))

    logger.info('crawl_momentum_quote Finished!')
    return True
