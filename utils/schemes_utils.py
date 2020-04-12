# -*- coding: utf-8 -*-
from marshmallow import Schema
from marshmallow import ValidationError

from log import _log as log


class AbstractScheme(Schema):

    @classmethod
    def is_valid(cls, data, many=None, partial=None, *args, **kwargs):
        try:
            validated_data = cls().load(data, many=many, partial=partial)
        except ValidationError as err:
            return err.messages, False
        except Exception as exc:
            log.debug('Exception: {0}!'.format(exc))
            return {'error': 'Something go wrong!'}, False
        else:
            log.debug('Valid data: {0}'.format(validated_data))
            return validated_data, True

    @classmethod
    def is_json_valid(cls, data, many=None, partial=None, *args, **kwargs):
        try:
            validated_data = cls().loads(data, many=many, partial=partial)
        except ValidationError as err:
            return err, False
        except Exception as exc:
            log.debug('Exception: {0}!'.format(exc))
            return {'error': 'Something go wrong!'}, False
        else:
            return validated_data, True