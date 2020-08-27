# -*- coding: utf-8 -*-
import argparse
import asyncio
import os

import sys

import aiohttp_jinja2
import jinja2
import uvloop
from aiohttp import web

from db.db import db_currency

from log import _log as log
from utils.task_utils import app_tasks_runner, app_task_close

from utils.settings_utils import conf
from utils.application_utils import auto_loader


async def app(argv):
    """
    python -m aiohttp.web -H localhost -P 8080 package.module:init_func
    python server.py -H 127.0.0.12 -P 8700
    adev runserver
    python app.py
    :param argv:
    :return:
    """
    settings = conf(filename=argv.settings)
    sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__))))
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # loop = uvloop.new_event_loop()
    # asyncio.set_event_loop(loop)
    # app = web.Application(logger=log, middlewares=[db_connection])
    app = web.Application(logger=log)
    app['db_currency'] = db_currency()
    app['settings'] = settings
    app.add_routes(
        auto_loader(
            installed_apps=settings.INSTALLED_APPS,
            filename='urls',
            parameter='ROUTERS'
        )
    )

    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader('{0}/templates'.format(os.getcwd()))
    )
    app_tasks_runner(app)
    # app.on_cleanup.append(app_task_close)
    return app


if __name__ == '__main__':
    parsed_args = argparse.ArgumentParser()

    parsed_args.add_argument('--port', '-P', action='store', dest='port',
                             default='8000', help='Set port default 8000')
    parsed_args.add_argument('--hostname', '-H', action='store', dest='host',
                             default='0.0.0.0', help='Set host default 0.0.0.0')
    parsed_args.add_argument('--path', action='store', dest='path',
                             help='Set path to socket file.')
    parsed_args.add_argument('--settings', '-s', action='store', dest='settings',
                             default='settings_base', help='Set settings file.')

    args = parsed_args.parse_args()
    os.environ.setdefault('SETTINGSFILE', '{0}'.format(args.settings))
    os.environ.setdefault('SETTINGSPATH', os.getcwd() + '/settings/{0}.py'.format(args.settings))
    app = app(args)
    web.run_app(
        app,
        port=args.port, host=args.host,
        access_log_format='%a "%r" %s %b "%{Referer}i" '
                          '"%{User-Agent}i" '
                          'time(microseconds): %D'
    )
    # setup(app)
