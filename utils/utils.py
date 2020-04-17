# -*- coding: utf-8 -*-
import datetime
import json
from aiohttp import ClientSession, ClientConnectorError
from aiohttp_retry import RetryClient

from utils.settings_utils import settings
from log import _log as log


class GetAndPreparedBanksData(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def bank_urls():
        """
        return {bank_url: bank name} for all registered banks in settings settings.BANK_API
        :return:
        """
        return {bank_map.get('url'): bank for bank, bank_map in settings.BANK_API.items()}

    @staticmethod
    def filter_currencies(currency_field_name, currencies, entry_data):
        return [item for item in entry_data if
                item.get(currency_field_name) in currencies]

    def currency_list(self, currency_field_name, currencies, dict_map, entry_data):
        items = self.filter_currencies(currency_field_name, currencies, entry_data)
        d = datetime.datetime.now() #- datetime.timedelta(days=1)
        return [
            {
                'date': d.strftime('%Y-%m-%d'),
                'bank': dict_map.get('bank_name'),
                'currency_name': item.get(dict_map.get('field')),
                'buy': item.get(dict_map.get('buy_field'), 0),
                'sale': item.get(dict_map.get('sale_field'), 0),
                # 'exchange_rate': item.get(dict_map.get('exchange_rate_field'), 0),
            } for item in items
        ]

    def currency_string(self, currency_field_name, currencies, dict_map, entry_data):
        items = self.filter_currencies(currency_field_name, currencies, entry_data)
        res = ''
        for cur in items:
            text = 'Currency text: ' + cur.get(dict_map.get('text')) + '\n' if dict_map.get(
                'text') else ''
            currency_name = cur.get(dict_map.get('field')) + '\n' if dict_map.get('field') else ''
            buy = 'Currency buy: ' + str(cur.get(dict_map.get('buy_field'))) + '\n' if dict_map.get(
                'buy_field') else ''
            sale = 'Currency sale: ' + str(
                cur.get(dict_map.get('sale_field'))) + '\n' if dict_map.get(
                'sale_field') else ''
            # ex_ch_field = 'Currency exchange: ' + str(
            #     cur.get(dict_map.get('exchange_rate_field'))) + '\n' if dict_map.get(
            #     'exchange_rate_field') else ''

            res += '{0}{1}{2}{3} \n'.format(
                text,
                currency_name,
                # ex_ch_field,
                buy,
                sale
            )
        return res

    def parse_json(self, bank_map, json_item, return_type='str'):
        items = json.loads(json_item) if isinstance(json_item, str) else json_item
        if bank_map.get('deep'):
            items = items[bank_map.get('deep') - 1].get(bank_map.get('deep_field_name'))

        if return_type == 'str':
            return self.currency_string(
                bank_map.get('field'),
                bank_map.get('currency_names'),
                bank_map,
                items
            )
        elif return_type == 'json':
            return self.currency_list(
                bank_map.get('field'),
                bank_map.get('currency_names'),
                bank_map,
                items
            )

    async def get_data_from_banks(self, return_type='str'):
        d = datetime.datetime.now() #- datetime.timedelta(days=1)
        res = '{0}\n'.format(
            datetime.datetime.now().strftime('%Y-%m-%d')
        ) if return_type == 'str' else {'date': d.strftime('%Y-%m-%d')}
        async with ClientSession() as session:
            for bank, bank_map in settings.BANK_API.items():
                try:
                    async with session.get(bank_map.get('url')) as resp:
                        if resp.status != 200:
                            if isinstance(res, str):
                                res += '{0}\n {1}\n'.format(
                                    bank, 'Can not gate data: {0}'.format(resp.status)
                                )
                            elif isinstance(res, dict):
                                log.debug(
                                    'Can not get data From BANK {0} : {1}'.format(
                                        bank,
                                        resp.status
                                    )
                                )
                        else:
                            json_bank_data = await resp.json()
                            if isinstance(res, str):
                                res += '{0}\n {1}\n'.format(
                                    bank, self.parse_json(
                                        bank_map,
                                        json_bank_data,
                                        return_type=return_type
                                    )
                                )
                            elif isinstance(res, dict):
                                res.update(
                                    {
                                        bank: self.parse_json(
                                            bank_map,
                                            json_bank_data,
                                            return_type=return_type
                                        )
                                    }
                                )
                except ClientConnectorError as e:
                    if isinstance(res, str):
                        res += '{0}\n {1}\n'.format(
                            bank, 'Can not get data: {0}'.format(e)
                        )
                    elif isinstance(res, dict):
                        log.debug('Can not get data: {0}'.format(e))
        return res
