# coding=utf-8
from flask import jsonify
from werkzeug.exceptions import HTTPException

def success_respond(data=None):
    return jsonify({'state_code': 0, 'state_message': 'success', 'data': data or {}})


def error_respond(msg, http_code=None, code=None):
    if isinstance(msg, (basestring, list, dict)):
        pass
    elif isinstance(msg, HTTPException) or issubclass(msg, HTTPException):
        http_code = msg.code
        code = getattr(msg, 'state_code')
        msg = msg.description
    r = jsonify({'state_code': code or 100, 'state_message': msg})
    r.status_code = http_code or 405
    return r
