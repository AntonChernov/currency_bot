# -*- coding: utf-8 -*-
from aiohttp import web

from currency_api import api

ROUTERS = [
    web.get('/api/ping', api.PingPongHandler, name='ping'),
    web.get('/api/currencies', api.GetCurrenciesFromRegBanks, name='cur'), #/api/currencies?type=dict
    web.get('/api/exchange', api.ExchangeRate, name='exchange'),
    web.get('/api/check-rate', api.CheckRate, name='check'),
    web.get('/api/cdts', api.CheckDictToStr, name='cdts'),
    # web.get('/api/median', api.CheckDictToStr, name='median'),
]