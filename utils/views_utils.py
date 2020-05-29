# -*- coding: utf-8 -*-
import datetime

from aiohttp import web
from aiohttp.abc import StreamResponse
from aiohttp.hdrs import METH_POST, METH_DELETE, METH_GET, METH_PATCH, METH_PUT, METH_OPTIONS
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from marshmallow import ValidationError

from utils.schemes_utils import AbstractScheme

from log import _log as log


def currency_rate_dict_to_str(obj_dict):
    res = ''
    for bank in obj_dict:
        res += '{0} {1} \n'.format(':date:', datetime.datetime.now().isoformat())
        res += '{0} Bank name: {1}\n'.format(':bank:', bank)
        for b_data in obj_dict[bank]:
            # res += '{0}Currency: {1}\n'.format('_'*1, b_data)
            res += '{0}Currency: {1}\n'.format(':moneybag:', b_data)
            # res += '{0}Sale price: {1}\n'.format('_'*2, obj_dict[bank][b_data]['sale'])
            res += '{0}Sale price: {1}\n'.format(':money_mouth_face:', obj_dict[bank][b_data]['sale'])
            # res += '{0}Buy price: {1}\n\n'.format('_'*2, obj_dict[bank][b_data]['buy'])
            res += '{0}Buy price: {1}\n\n'.format(':money_mouth_face:', obj_dict[bank][b_data]['buy'])
        res += '+'*20
        res += '\n'
    return res


class BaseAPIView(web.View):
    """
    Base class for API Views
    NOTE! "validation_class" and "model" must be set in child class!!!
    """
    allowed_methods = [METH_POST, METH_DELETE, METH_GET, METH_PATCH, METH_PUT, METH_OPTIONS]
    limit = 25
    offset = 0
    paginate = True
    lookup_field = 'id'
    filtered_fields = []
    # TODO "lookup_field" --> not work need fix!!!
    # TODO add permission classes

    async def _iter(self) -> StreamResponse:
        if self.request.method not in self.allowed_methods:
            self._raise_allowed_methods()
        method = getattr(self, self.request.method.lower(), None)
        if method is None:
            self._raise_allowed_methods()
        resp = await method()
        return resp

    async def pagination(self, query):
        if self.paginate:
            limit = self.request.query.get('limit', self.limit)
            offset = self.request.query.get('offset', self.offset)
            res = await query.limit(limit).offset(offset).gino.all()
        else:
            res = await query.gino.all()
        return res

    def _raise_allowed_methods(self) -> None:
        allowed_methods = {
            m for m in self.allowed_methods if hasattr(self, m.lower())}
        raise HTTPMethodNotAllowed(self.request.method, allowed_methods)

    @property
    def validation_class(self):
        """Property for validation class(from schemes)"""
        return self.validation_class

    @validation_class.setter
    def validation_class(self, val):
        if not isinstance(val, AbstractScheme):
            raise ValidationError('Validation class must be instance of AbstractScheme!')
        self.validation_class = val

    @property
    def model(self):
        """Property for set the model."""
        return self.model

    def filtered(self):
        """
        Check filtered fields and return query with filter
        :return:
        """
        if self.filtered_fields:
            return None

    async def get(self):
        _id = self.request.match_info.get('id')
        # filtered_ = self.filtered_fields
        if not _id:
            # data = await self.model.query.gino.all() #if not self.filtered_fields else await self.model.query.filter
            data = await self.pagination(self.model.query) #if not self.filtered_fields else await self.model.query.filter
            log.debug('{0}'.format(data))
            return web.json_response({'items': self.validation_class.dump(data, many=True)})
        data = await self.model.query.where(self.model.id == int(_id)).gino.first()
        log.debug('{0}'.format(data))
        return web.json_response({'items': self.validation_class.dump(data)})

    async def post(self):
        data, is_valid = self.validation_class.is_valid(await self.request.json() if self.request.can_read_body else {})
        if not is_valid:
            log.debug('data is: {0}'.format(data))
            return web.json_response(data, status=400)
        log.debug('data is: {0}'.format(data))
        dt = await self.model.create(**data)
        return web.json_response(self.validation_class.dump(dt), status=201)

    async def patch(self):
        _id = self.request.match_info['id']
        d = await self.model.query.where(self.model.id == int(_id)).gino.first()
        data, is_valid = self.validation_class.is_valid(await self.request.json() if self.request.can_read_body else {})
        if not is_valid:
            log.debug('Validation error!: {0}'.format(is_valid))
            return web.json_response(data, status=400)
        log.debug('All ok! {0}'.format(data))
        await d.update(**data).apply()
        return web.json_response(self.validation_class.dump(d))

    async def delete(self):
        _id = self.request.match_info['id']
        d = await self.model.query.where(self.model.id == int(_id)).gino.first()
        await d.delete()
        return web.json_response(status=200)

    async def put(self):
        return await self.patch()

    async def option(self):
        default_headers = {
            'Access-Control-Request-Method': ','.join(method.capitalize() for method in self.allowed_methods),
            'Content-Type': 'text/plain'

        }
        return web.Response(status=204, headers=default_headers)