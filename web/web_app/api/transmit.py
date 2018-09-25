# coding=utf-8
import json
from web_app import app
from web_app.api import api
from flask import request, Response
import requests
from web_app import utils as _
from web_app.utils import ParseTokenConfig



def _get_resp_headers(resp):
    resp_headers = []
    for name, value in resp.headers.items():
        if name.lower() in ('content-length', 'connection',
                            'content-encoding'):
            continue
        resp_headers.append((name, value))
    return resp_headers



@api.route('/trackings', methods=['get', 'post'])
@api.route('/trackings/<id>', methods=['get', 'patch', 'delete'])
def transmit(id=None):
    hc = ParseTokenConfig()
    app_host = hc.get_transmit_config()
    del hc
    app_host = app_host[:-1] if app_host.endswith('/') else app_host

    base_url = app_host + '/trackings' + ('' if not id else '/{}'.format(id))

    uc = ParseTokenConfig()
    token_config = uc.get_header_config()
    del uc

    get_config = token_config.get(request.args.get('token', None), None)
    if not get_config:
        return _.error_respond(msg='Token not right', http_code=403)
    token = get_config.get('x-auth-token')
    broker_id = int(get_config.get('broker_id'))
    client = get_config.get('client')
    Installation_ID = get_config.get('Installation-ID')

    if [k+'='+v for k, v in request.args.items() if k != 'token']:
        url = base_url + '?' + reduce(lambda x,y:  x+'&'+y, [k+'='+v for k, v in request.args.items() if k != 'token'])
    else:
        url = base_url

    headers = dict(request.headers)
    headers.update({'Host': app_host, 'x-auth-token': token, 'client': client, 'Installation-ID': Installation_ID})
    headers.pop('Host')


    if request.method.lower() == 'get':
        resp = getattr(requests, request.method.lower())(url=url, headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)

    elif request.method.lower() == 'post':
        json_data = request.get_json()
        json_data.update({'broker_id': broker_id})
        resp = getattr(requests, request.method.lower())(url=url, json=json_data, headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)

    elif request.method.lower() == 'patch':
        resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)

    elif request.method.lower() == 'delete':
        resp = getattr(requests, request.method.lower())(url=url, headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)



@api.route('/location_events', methods=['post'])
def location_events(id=None):
    hc = ParseTokenConfig()
    app_host = hc.get_transmit_config()
    del hc
    app_host = app_host[:-1] if app_host.endswith('/') else app_host

    base_url = app_host + '/location_events' + ('' if not id else '/{}'.format(id))

    uc = ParseTokenConfig()
    token_config = uc.get_header_config()
    del uc

    get_config = token_config.get(request.args.get('token', None), None)
    if not get_config:
        return _.error_respond(msg='Token not right', http_code=403)
    token = get_config.get('x-auth-token')
    client = get_config.get('client')
    Installation_ID = get_config.get('Installation-ID')

    if [k+'='+v for k, v in request.args.items() if k != 'token']:
        url = base_url + '?' + reduce(lambda x,y:  x+'&'+y, [k+'='+v for k, v in request.args.items() if k != 'token'])
    else:
        url = base_url

    headers = dict(request.headers)
    headers.update({'Host': app_host, 'x-auth-token': token, 'client': client, 'Installation-ID': Installation_ID})
    headers.pop('Host')


    if request.method.lower() == 'post':
        resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

        resp_headers = _get_resp_headers(resp)

        return Response(resp, status=resp.status_code, headers=resp_headers)
