# coding=utf-8
from web_app.api import api
from web_app import logger
from flask import request, Response
import requests
from web_app import utils as _
from web_app.utils import ParseTokenConfig, signature_authentication



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
@signature_authentication(sub_url='/trackings', request=request)
def transmit(id=None):
    hc = ParseTokenConfig()
    sys = hc.get_transmit_config()
    app_host = sys.get('host')
    del hc
    app_host = app_host[:-1] if app_host.endswith('/') else app_host

    base_url = app_host + '/trackings' + ('' if not id else '/{}'.format(id))

    uc = ParseTokenConfig()
    token_config = uc.get_header_config()
    del uc

    get_config = token_config.get(request.args.get('accessKey', None), None)
    if not get_config:
        return _.error_respond(msg='accessKey not right', http_code=403)
    token = get_config.get('x-auth-token')
    broker_id = int(get_config.get('broker_id'))
    client = get_config.get('client')
    Installation_ID = get_config.get('Installation-ID')

    if [k+'='+v for k, v in request.args.items() if k != 'accessKey' and k != 'signature' and k != 'timestamp']:
        url = base_url + '?' + reduce(lambda x,y:  x+'&'+y, [k+'='+v for k, v in request.args.items() if k != 'accessKey' and k != 'signature' and k != 'timestamp'])
    else:
        url = base_url

    headers = dict(request.headers)
    headers.update({'Host': app_host, 'x-auth-token': token, 'client': client, 'Installation-ID': Installation_ID})
    headers.pop('Host')

    exc = None

    try:
        if request.method.lower() == 'get':
            args_key_set = set([k for k in request.args.keys() if k != 'accessKey' and k != 'signature' and k != 'timestamp'])
            if (id == None) and ('broker_id' not in args_key_set) and ('carrier_id' not in args_key_set):
                url = url + '?' + 'broker_id={}'.format(broker_id) if '?' not in url else url + '&' + 'broker_id={}'.format(broker_id)
            resp = getattr(requests, request.method.lower())(url=url, headers=headers)

            resp_headers = _get_resp_headers(resp)

        elif request.method.lower() == 'post':
            json_data = request.get_json()
            json_data.update({'broker_id': broker_id})
            resp = getattr(requests, request.method.lower())(url=url, json=json_data, headers=headers)

            resp_headers = _get_resp_headers(resp)

        elif request.method.lower() == 'patch':
            resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

            resp_headers = _get_resp_headers(resp)

        elif request.method.lower() == 'delete':
            resp = getattr(requests, request.method.lower())(url=url, headers=headers)

            resp_headers = _get_resp_headers(resp)
    except Exception as e:
        exc = e

    logger.debug('Method: {}| Headers: {}| Url: {}| Data: {}| Http code: {}| Exception: {}'.format(request.method, request.headers, request.url,
                                                                     request.get_json(), (exc.http_status or 500 if hasattr(exc, 'http_status') else None) if exc else resp.status_code, str(exc)))

    return Response(resp if not exc else str(exc),
                    status=resp.status_code if not exc else (exc.http_status or 500 if hasattr(
                        exc,
                        'http_status') else 500), headers=resp_headers if not exc else None)


@api.route('/location_events', methods=['post'])
@signature_authentication(sub_url='/location_events', request=request)
def location_events(id=None):
    hc = ParseTokenConfig()
    sys = hc.get_transmit_config()
    app_host = sys.get('host')
    del hc
    app_host = app_host[:-1] if app_host.endswith('/') else app_host

    base_url = app_host + '/location_events' + ('' if not id else '/{}'.format(id))

    uc = ParseTokenConfig()
    token_config = uc.get_header_config()
    del uc

    get_config = token_config.get(request.args.get('accessKey', None), None)
    if not get_config:
        return _.error_respond(msg='accessKey not right', http_code=403)
    token = get_config.get('x-auth-token')
    client = get_config.get('client')
    Installation_ID = get_config.get('Installation-ID')

    if [k+'='+v for k, v in request.args.items() if k != 'accessKey' and k != 'signature' and k != 'timestamp']:
        url = base_url + '?' + reduce(lambda x,y:  x+'&'+y, [k+'='+v for k, v in request.args.items() if k != 'accessKey' and k != 'signature' and k != 'timestamp'])
    else:
        url = base_url

    headers = dict(request.headers)
    headers.update({'Host': app_host, 'x-auth-token': token, 'client': client, 'Installation-ID': Installation_ID})
    headers.pop('Host')

    exc = None

    try:
        if request.method.lower() == 'post':
            resp = getattr(requests, request.method.lower())(url=url, json=request.get_json(), headers=headers)

            resp_headers = _get_resp_headers(resp)
    except Exception as e:
        exc = e

    logger.debug('Method: {}| Headers: {}| Url: {}| Data: {}| Http code: {}| Exception: {}'.format(request.method,
                                                                                                   request.headers,
                                                                                                   request.url,
                                                                                                   request.get_json(), (
                                                                                                   exc.http_status or 500 if hasattr(
                                                                                                       exc,
                                                                                                       'http_status') else None) if exc else resp.status_code,
                                                                                                   str(exc)))
    return Response(resp if not exc else str(exc), status=resp.status_code if not exc else (exc.http_status or 500 if hasattr(
                                                                                                       exc,
                                                                                                       'http_status') else 500), headers=resp_headers if not exc else None)
