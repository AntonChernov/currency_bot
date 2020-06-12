# -*- coding: utf-8 -*-
"""
Migrations create alembic revision -m "Create viever_devices and template dbs" --autogenerate --head head
Accept migrations: alembic upgrade head
"""
import copy
import datetime

import motor.motor_asyncio

from utils.settings_utils import settings
from log import _log as log


def db_currency(*args, **kwargs):
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE.get('client'))
    db = client[settings.DATABASE.get('db_name')]
    collection = db[settings.DATABASE.get('collection')]
    return collection


async def save_data(connection, data):
    c_data = copy.deepcopy(data)
    date = c_data.pop('date')
    for item_name, item_values in c_data.items():
        for item_val in item_values:
            res = await connection.find_one(
                {
                    'date': date,
                    'currency_name': item_val.get('currency_name'),
                    'bank': item_val.get('bank'),

                }
            )
            item_val['buy'] = round(float(item_val.get('buy', 0)), 3)
            item_val['sale'] = round(float(item_val.get('sale', 0)), 3)
            log.debug(res)
            if res and res['_id']:
                await connection.update_one({'_id': res['_id']}, {'$set': item_val})
                # log.debug(f'item val {item_val}')
                log.debug('Updated one item: {0}'.format(res['_id']))
            else:
                ins = await connection.insert_one(item_val)
                log.debug('Insert new item: {0}'.format(ins.inserted_id))
    log.debug('Save finished!')


def prepare_detail_bank_data(bank_name, data):
    return [item for item in data if item['bank'] == bank_name]


def prepare_detail_currencies(currencies, detail_bank_data):
    res = {}
    for bank, val in detail_bank_data.items():
        bank_d = {}
        # log.debug('------------------ \n {0}'.format(bank_d))
        for cur in currencies:
            cur_bank = [item for item in val if item['currency_name'] == cur]
            # log.debug('------------------ \n {0}'.format(cur_bank))
            if len(cur_bank) == 2:
                bank_d.update({
                    cur: {
                        'buy': round(float(cur_bank[1].get('buy')) -
                                     float(cur_bank[0].get('buy')), 4),
                        'sale': round(float(cur_bank[1].get('sale')) -
                                      float(cur_bank[0].get('sale')), 4),
                        # 'exchange_rate': round(float(
                        #     cur_bank[1].get('exchange_rate')
                        # ) - float(cur_bank[0].get('exchange_rate')), 4),
                    }
                })
            elif len(cur_bank) == 0:
                bank_d.update({
                    cur: {
                        'buy': round(float(0), 4),
                        'sale': round(float(0), 4),
                        # 'exchange_rate': round(float(0), 4),
                    }
                })
            elif len(cur_bank) == 1:
                bank_d.update({
                    cur: {
                        'buy': round(float(cur_bank[0].get('buy')), 4),
                        'sale': round(float(cur_bank[0].get('sale')), 4),
                        # 'exchange_rate': round(float(cur_bank[0].get('exchange_rate')), 4),
                    }
                })
        res.update({bank: bank_d})
    return res


async def get_exchange_rate(connection):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    pipe_line = connection.find(
        {
            'date': {'$gte': yesterday.strftime('%Y-%m-%d')}
        }
    ).sort([('bank', -1), ('currency_name', 1), ('date', 1)])
    banks = await pipe_line.distinct('bank')
    currencies = await pipe_line.distinct('currency_name')
    result = []
    rresult = {}

    async for res in pipe_line:
        result.append(
            {
                "date": res['date'],
                "bank": res['bank'],
                "currency_name": res['currency_name'],
                "buy": res['buy'],
                "sale": res['sale'],
                # "exchange_rate": res['exchange_rate']
            }
        )
    for i in banks:
        rresult.update({i: prepare_detail_bank_data(i, result)})
    log.debug(rresult)
    res = prepare_detail_currencies(currencies, rresult)

    return res