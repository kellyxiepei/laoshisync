# -*- coding: utf-8 -*-
#
#      File: config.py
#   Project: laoshisync
#    Author: Xie Wangyi
#
#   Copyright (c) 2017 Laoshishuo. All rights reserved.
import datetime
import json
import os
import time

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
                                      u'laoshi_sync_inbox',
                                      file_name)
        if os.path.isfile(full_file_name):
            logger.info(file_name + u' already exsits.')
            continue
        url = b['preview_url']
        open(full_file_name, "wb").close()  # create the file as mutex signal
        logger.info(u'Downloading "{}"'.format(file_name))
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(full_file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            else:
                raise IOError('Http return not 200,{},{}'.format(r.status_code,
                                                                 file_name))
        except IOError as e:
            logger.error(repr(e))
            os.remove(full_file_name)

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
                                      u'laoshi_sync_inbox',
                                      file_name)
        if os.path.isfile(full_file_name):
            logger.info(file_name + u' already exsits.')
            continue
        open(full_file_name, "wb").close()  # create the file as mutex signal
        logger.info(u'Downloading "{}"'.format(file_name))
        try:
            r = requests.get(
                'https://api.momentumdash.com/feed/bulk?'
                'syncTypes=quote&localDate={}'.format(date),
                headers=dict(authorization=KEY))
            if r.status_code == 200:
                res_json = r.json()['quotes'][0]
                with open(full_file_name, 'w') as f:
                    f.write(u'{} \r\n -- By {}'.format(
                        res_json['body'],
                        res_json[
                            'source']).encode('utf-8'))
            else:
                raise IOError('Http return not 200,{},{}'.format(r.status_code,
                                                                 file_name))
        except IOError as e:
            logger.error(repr(e))
            os.remove(full_file_name)

    logger.info('crawl_momentum_quote Finished!')
    return True


@celeryapp.task(
    bind=True,
    default_retry_delay=10,
    name='laoshisync.crawl_bing_wallpaper')
def crawl_bing_wallpaper(self):
    today = datetime.date.today()

    for i in range(7):
        date = (today + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
        file_name = u'{} - bing_wallpaper.txt'.format(date)

        full_file_name = os.path.join(unicode(WORKING_DIR),
                                      u'laoshi_sync_inbox',
                                      file_name)
        if os.path.isfile(full_file_name):
            logger.info(file_name + u' already exsits.')
            continue
        open(full_file_name, "wb").close()  # create the file as mutex signal
        try:
            logger.info(u'Downloading "{}"'.format(file_name))
            with requests.session() as sess:
                sess.get('https://www.bing.com/?'
                         'FORM=&setmkt=en-us&setlang=en-us')
                r1 = sess.get(
                    'https://www.bing.com/HPImageArchive.aspx?'
                    'format=js&idx={}&n=1&nc={}&pid=hp&intlF=&'
                    'quiz=1&fav=1'.format(i, time.time()))

                sess.get('https://www.bing.com/?'
                         'FORM=&setmkt=zh-cn&setlang=zh-cn')

                r2 = sess.get(
                    'https://www.bing.com/HPImageArchive.aspx?'
                    'format=js&idx={}&n=1&nc={}&pid=hp&intlF=&'
                    'quiz=1&fav=1'.format(i, time.time()))

                if r1.status_code == 200 and r2.status_code == 200:
                    r1_json = r1.json()
                    r2_json = r2.json()
                    with open(full_file_name, 'w') as f:
                        f.write(u'{}\r\n{}\r\n'.format(
                            r1_json['images'][0]['copyright'],
                            r2_json['images'][0]['copyright']).encode('utf-8'))
                else:
                    raise IOError(
                        'Http return not 200,{},{},{}'.format(r1.status_code,
                                                              r2.status_code,
                                                              file_name))
                image_file_name = u'{} - bing_wallpaper.jpg'.format(date)
                full_image_file_name = os.path.join(unicode(WORKING_DIR),
                                                    u'laoshi_sync_inbox',
                                                    image_file_name)

                logger.info(u'Downloading "{}"'.format(image_file_name))

                r = sess.get(
                    'https://www.bing.com' + r1_json['images'][0]['url'],
                    stream=True)
                if r.status_code == 200:
                    with open(full_image_file_name, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                else:
                    raise IOError('Http return not 200,{},{}'.format(
                        r.status_code,
                        image_file_name))
        except IOError as e:
            logger.error(repr(e))
            os.remove(full_file_name)

    logger.info('crawl_bing_wallpaper Finished!')
    return True
