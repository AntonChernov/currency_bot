# -*- coding: utf-8 -*-
import os

# Installed apps

INSTALLED_APPS = [
    'currency_api',
]

BANK_API = {
    'NBU': {
        'bank_name': 'NBU',
        # 'url': 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date=20200324&json',
        'url': 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json',
        'deep': 0,
        'field': 'cc',
        'currency_names': ('EUR', 'USD'), # currency_names tuple and must be lice in ISO 4217
        'buy_field': None,
        'sale_field': 'rate',
        # 'exchange_rate_field': 'rate', # Field not use any more and should be delete
        'date': 'exchangedate',
        'text': 'txt'
    },
    'Privat_bank': {
        'bank_name': 'Privat_bank',
        'url': 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5',
        'deep': 0,
        'field': 'ccy',
        'currency_names': ('EUR', 'USD'),
        'buy_field': 'buy',
        'sale_field': 'sale',
        # 'exchange_rate_field': None, # Field not use any more and should be delete
        'date': None,
        'text': None
    },
    'NBP': {
        'bank_name': 'NBP',
        'url': 'http://api.nbp.pl/api/exchangerates/tables/c/?format=json',
        'deep': 1,
        'deep_field_name': 'rates',
        'field': 'code',
        'currency_names': ('EUR', 'USD'),
        'buy_field': 'bid',
        'sale_field': 'ask',
        # 'exchange_rate_field': None, # Field not use any more and should be delete
        'date': None,
        'text': 'currency'
    },
}

# End of installed apps

# Telegram bot token
TELEGRAM_TOKEN = 'some token'
# End Telegram bot token

### Databases

REDIS_CLUSTER = [
    {'host': '127.0.0.1', 'port': '6379'},
]

REDIS_CLUSTER_MODE = False

DATABASE = {
    'client': os.environ.get("MONGO_DB_URI", "mongodb://localhost:27017"),
    # 'client': 'mongodb://host1,host2/?replicaSet=my-replicaset-name',
    'db_name': 'currency',
    'collection': 'banks'
}

#### Task block
TASKS_SETTING = {
    'delay': 600, # Default task sleep :) time
    'include': [
        'tasks.tasks'
    ]
}

####

#### End of databases block

CELERY = {
    'NAME': 'mark_tool',
    'USE_DB': True,
    'CONF': {
        # 'broker_url': 'redis://31.168.228.102:6379/0',
        'broker_url': os.environ.get('CELERY_BROKER', 'redis://localhost:6379/12'),
        # 'result_backend': 'redis://31.168.228.102:6379/1',
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        # 'imports': 'auto',
        'task_serializer': 'json',
        'accept_content': ['json'],  # Ignore other content
        'result_serializer': 'json',
        'timezone': 'Europe/Oslo',
        'enable_utc': True,
        'include': [
            'push_service.tasks',
            'audience_service.tasks'
        ],
        'task_routes': {
            'push.*': {'queue': 'push'},
            'audience.druid.*': {'queue': 'druid'},
            'audience.*': {'queue': 'audience'},
            #'ditto.*': {'queue': 'ditto'},
            # 'ugc.*': {'queue': 'ams'},
#            '*': {'queue': 'celery'},
        }
    }
}
# CELERY BLOCK END
