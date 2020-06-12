# -*- coding: utf-8 -*-
import datetime
import calendar

import aiohttp
from aiohttp import web

from db.db import save_data, get_exchange_rate
from log import _log as log
from utils.utils import GetAndPreparedBanksData
from utils.views_utils import currency_rate_dict_to_str


class PingPongHandler(web.View):

    async def get(self, ):
        return web.json_response({'Ping': 'Pong'})


class GetCurrenciesFromRegBanks(web.View):

    async def get(self):
        req_type = self.request.rel_url.query.get('type')
        if not req_type or req_type == 'str':
            res = await GetAndPreparedBanksData().get_data_from_banks()
            return web.Response(body=res)
        else:
            res = await GetAndPreparedBanksData().get_data_from_banks(return_type='json')
            await save_data(self.request.app['db_currency'], res)
            return web.json_response(data=res)


class CheckRate(web.View):

    async def get(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        pipe_line = self.request.app['db_currency'].find(
            {
                'date': {'$gte': yesterday.strftime('%Y-%m-%d')}
            }
        ).sort([('bank', -1), ('currency_name', 1), ('date', 1)])
        data = []
        async for res in pipe_line:
            data.append(
                {
                    "date": res['date'],
                    "bank": res['bank'],
                    "currency_name": res['currency_name'],
                    "buy": res['buy'],
                    "sale": res['sale'],
                    # "exchange_rate": res['exchange_rate']
                }
            )
        return web.json_response(data=data)


class ExchangeRate(web.View):

    async def get(self):
        data = await get_exchange_rate(self.request.app['db_currency'])
        return web.json_response(data=data)


class CheckDictToStr(web.View):

    async def get(self):
        data = await get_exchange_rate(self.request.app['db_currency'])
        res = currency_rate_dict_to_str(data)
        return web.Response(body=res)


class MonthMedian(web.View):

    async def get(self):
        year_month = self.request.rel_url.query.get('date')
        _, end_date = calendar.monthrange(
            int(datetime.datetime.strptime(year_month, '%Y-%m').year),
            int(datetime.datetime.strptime(year_month, '%Y-%m').month)
        )
        from_date = datetime.datetime.strptime(year_month, '%Y-%m-%d')
        to_date = datetime.datetime.strptime(year_month, '%Y-%m-%d')
        pipe_line = self.request.app['db_currency'].find(
            {
                'date': {
                    '$gte': from_date.strftime('%Y-%m-%d'),
                    '$lte': to_date.replace(day=end_date).strftime('%Y-%m-%d')
                }
            }

        )
        data = []
        async for item in pipe_line:
            pass
        res = currency_rate_dict_to_str(data)
        return web.Response(body=res)
