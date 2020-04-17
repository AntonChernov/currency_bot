# -*- coding: utf-8 -*-
import asyncio
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor

from db.db import save_data
from utils.task_utils import TaskDecorator
from utils.utils import GetAndPreparedBanksData
from log import _log as log


# class TaskGetBankData(object):
#     def __init__(self, app, execute_after=settings.TASKS_SETTING.get('delay', 60)):
#         self.app = app
#         self.execute_after = execute_after
#         self.loop = asyncio.get_event_loop()
#         self.tasks = deque([])
#
#     def add_task(self, func, exec_after, *args, **kwargs):
#         self.tasks.append((func, exec_after, args, kwargs))
#
#     async def process_queue(self, *args, **kwargs):
#         obj = GetAndPreparedBanksData()
#         while True:
#             res = await obj.get_data_from_banks(return_type='json')
#             await save_data(self.app['db_currency'], res)
#             await asyncio.sleep(self.execute_after)
#
#     async def start_background_tasks(self, *args, **kwargs):
#         self.app['dispatch'] = self.app.loop.create_task(self.process_queue())
#
#     async def cleanup_background_tasks(self, *args, **kwargs):
#         self.app['dispatch'].cancel()
#         await self.app['dispatch']


# @TaskDecorator(10)
# async def task_test(app, a_name='Anton', a='Fullname'):
#     log.debug('Op Jigurda {0} {1}'.format(a_name, a))


@TaskDecorator()
async def task_get_bank_data(app, obj=GetAndPreparedBanksData()):
    res = await obj.get_data_from_banks(return_type='json')
    await save_data(app['db_currency'], res)


# @TaskDecorator(1)
# async def task_print_test(app, *args, **kwargs):
#     log.debug('hello')

