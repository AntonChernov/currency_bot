# -*- coding: utf-8 -*-
from marshmallow import fields
from marshmallow import validate

from utils.schemes_utils import AbstractScheme


class GetNBUCurrencyScheme(AbstractScheme):
    r030 = fields.Int()
    txt = fields.Str()
    rate = fields.Float()
    cc = fields.Str()
    exchangedate = fields.Date()

