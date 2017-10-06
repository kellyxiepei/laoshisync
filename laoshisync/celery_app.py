# -*- coding: utf-8 -*-
#
#      File: config.py
#   Project: laoshisync
#    Author: Xie Wangyi
#
#   Copyright (c) 2017 Laoshishuo. All rights reserved.

from celery import Celery

celery = Celery('laoshisync')

celery.config_from_object('celery_config')
