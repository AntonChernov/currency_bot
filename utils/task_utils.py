# -*- coding: utf-8 -*-
import asyncio
import importlib
import concurrent.futures
import time
from asyncio import shield

import aiojobs
from aiojobs.aiohttp import spawn
from functools import wraps

from log import _log as log
from utils.settings_utils import settings


class TaskDecorator(object):

    def __init__(self, period=None, protected=False):
        self.protected = protected
        self.period = period if period else settings.TASKS_SETTING.get('delay', 60)
        self.loop = None
        self.args = None
        self.kwargs = None

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            scheduler = await aiojobs.create_scheduler()
            await scheduler.spawn(func_executor(func, *args, **kwargs))

        async def func_executor(func, *args, **kwargs):
            while True:
                # if self.protected:
                #     await shield(asyncio.create_task(func(*args, **kwargs)))
                # else:
                asyncio.create_task(func(*args, **kwargs))
                await asyncio.sleep(self.period)
        return wrapper


def app_tasks_runner(app):
    task_modules = settings.TASKS_SETTING.get('include')
    for module in task_modules:
        imp_mod = importlib.import_module(module)
        task_func = [
            func for func in dir(imp_mod) if
            func.startswith('task_')
            and not func.startswith('__')
        ]
        for task in task_func:
            fnc = getattr(imp_mod, task)
            app.on_startup.append(fnc)


def app_task_close(app):
    for task in asyncio.all_tasks():
        log.debug('Task close: {0}'.format(task))
        task.cancel()
        log.debug('Task closed!')


# def periodic(period):
#     def scheduler(fcn):
#
#         async def wrapper(*args, **kwargs):
#
#             while True:
#                 asyncio.create_task(fcn(*args, **kwargs))
#                 await asyncio.sleep(period)
#
#         return wrapper
#
#     return scheduler
