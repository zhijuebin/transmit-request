# coding=utf-8
from flask import Blueprint
from werkzeug.exceptions import HTTPException
from flask_restful import Api


__all__ = ['api']

api = Blueprint('api_1_0', __name__)


api.register_error_handler(HTTPException, lambda x: _.error_respond(
    msg=str(x),
    http_code=getattr(x, 'code', 501),
    code=getattr(x, 'state_code', 1)
))


class NoErrorHandlerApi(Api):
    def _has_fr_route(self):
        return False


import transmit
