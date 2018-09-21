# coding=utf-8
from flask import jsonify
import json
from web_app import app
from web_app.api import api
from flask import request, Response
import requests
from web_app import utils as _


app_token_dict = json.loads(app.config.get('AUTHENTICATION_TOKEN_DICT'))

app_host = app.config.get('TRANSMIT_HOST')
app_host = app_host[:-1] if app_host.endswith('/') else app_host


def _get_resp_headers(resp):
    resp_headers = []
    for name, value in resp.headers.items():
        if name.lower() in ('content-length', 'connection',
                            'content-encoding'):
            continue
        resp_headers.append((name, value))
    return resp_headers



@api.route('/trackings', methods=['get', 'post'])
@api.route('/trackings/<id>', methods=['get', 'patch'])
def transmit(id=None):

    base_url = app_host + '/trackings' + ('' if not id else '/{}'.format(id))

    get_token = app_token_dict.get(request.args.get('token', None), None)
    if not get_token:
        return _.error_respond(msg='Token not right', http_code=403)

    if [k+'='+v for k, v in request.args.items() if k != 'token']:
        url = base_url + '?' + reduce(lambda x,y:  x+'&'+y, [k+'='+v for k, v in request.args.items() if k != 'token'])
    else:
        url = base_url

    headers = dict(request.headers)
    headers.update({'Host': app_host, 'x-auth-token': get_token})
    headers.pop('Host')


    if request.method.lower() == 'get':
        resp = getattr(requests, request.method.lower())(url=url, headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)

    elif request.method.lower() == 'post':
        resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)

    elif request.method.lower() == 'patch':
        resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)
