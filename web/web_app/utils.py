# coding=utf-8
from web_app import app
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



import os
from xml.parsers.expat import ParserCreate


class ParseTokenConfig(object):

    class HeadersSaxHandler(object):
        def __init__(self):
            self.users = {}
            self.current_user_token = ''
            self.current_tag = ''
            self.user_child_tags = ['x-auth-token', 'Installation-ID', 'client', 'broker_id', 'secretKey']

        def start_element(self, name, attrs):
            if name == 'user':
                self.current_tag = name
                self.current_user_token = attrs.get('token', '')
                self.users.update({self.current_user_token: {}})
            if name in self.user_child_tags:
                self.current_tag = self.current_tag + '||' + name

        def char_data(self, text):
            current_tag = self.current_tag.split('||')[-1]
            if current_tag in self.user_child_tags:
                self.users[self.current_user_token].update({current_tag: text})

        def end_element(self, name):
            if name == 'user':
                self.current_tag = ''
            if name in self.user_child_tags:
                self.current_tag = reduce(lambda x, y: x + '||' + y, self.current_tag.split('||')[: -1])


    class SysSaxHandler(object):
        def __init__(self):
            self.sys = {}

        def start_element(self, name, attrs):
            if name == 'transmit':
                self.sys.update({k:v for k, v in attrs.items()})

        def char_data(self, text):
            pass

        def end_element(self, name):
            pass


    def __init__(self):
        self.xml_path = reduce(lambda x,y: os.path.join(x, y), ['config_file', 'xml', 'token_config.xml'])
        self.f = None


    def get_header_config(self):
        self.handler = self.HeadersSaxHandler()
        self.parser = ParserCreate()
        self.parser.returns_unicode = True
        self.parser.StartElementHandler = self.handler.start_element
        self.parser.EndElementHandler = self.handler.end_element
        self.parser.CharacterDataHandler = self.handler.char_data

        self.f = open(self.xml_path, 'r')
        self.parser.ParseFile(self.f)
        self.f.close()

        return self.handler.users


    def get_transmit_config(self):
        self.handler = self.SysSaxHandler()
        self.parser = ParserCreate()
        self.parser.returns_unicode = True
        self.parser.StartElementHandler = self.handler.start_element
        self.parser.EndElementHandler = self.handler.end_element
        self.parser.CharacterDataHandler = self.handler.char_data

        self.f = open(self.xml_path, 'r')
        self.parser.ParseFile(self.f)
        self.f.close()

        return self.handler.sys


    def __del__(self):
        if not self.f.closed:
            self.f.close()


import logging
from logging import handlers

_HDLR = None

def _hdlr():
    global _HDLR
    if _HDLR is None:
        hdlr = handlers.TimedRotatingFileHandler('logs/main.log', when='D', interval=1)
        formatter = logging.Formatter('%(asctime)s||%(levelname)s||%(message)s')
        hdlr.setFormatter(formatter)
        _HDLR = hdlr
    return _HDLR


def get_logger(name):
    logger = logging.getLogger(name)
    if app.config.get('LOGGER_DEBUG_MODE'):
        logging.basicConfig(
            level=app.config.get('LOGGER_DEBUG_LEVEL'), format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
        )

    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        logger.setLevel(app.config.get('LOGGER_DEBUG_LEVEL'))
        logger.addHandler(_hdlr())

    return logger


import hashlib
import functools
import datetime

def signature_authentication(sub_url, request):
    def decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kw):
            hc = ParseTokenConfig()
            sys = hc.get_transmit_config()
            expired_seconds = int(sys.get('expired_seconds'))
            secretKey = sys.get('secretKey')
            del hc

            uc = ParseTokenConfig()
            token_config = uc.get_header_config()
            del uc

            get_config = token_config.get(request.args.get('accessKey', None), None)
            if not get_config:
                return _.error_respond(msg='accessKey not right', http_code=403)

            secretKey_g = get_config.get('secretKey', None)
            if secretKey_g:
                secretKey = secretKey_g

            re_args = {k: v for k, v in request.args.items()}
            now = datetime.datetime.now()
            if ('timestamp' not in re_args) or ('signature' not in re_args):
                return error_respond(msg='no timestamp or signature in your request url', http_code=400)
            sign = re_args['signature']

            try:
                args_timestamp = int(re_args['timestamp'])
                args_time = datetime.datetime.fromtimestamp(args_timestamp)
            except:
                return error_respond(msg='error timestamp', http_code=403)

            args_time_b = now + datetime.timedelta(seconds=-expired_seconds)
            args_time_e = now + datetime.timedelta(seconds=expired_seconds)
            if not (args_time >= args_time_b and args_time <= args_time_e):
                return error_respond(msg='expired request', http_code=403)

            # url
            url = request.url
            index_b = url.find(sub_url)
            index_e = url.find('?')
            base_auth_url = url[index_b: index_e]

            # args one
            if [k + '=' + v for k, v in re_args.items() if k != 'signature']:
                args_one_url = '?' + reduce(lambda x, y: x + '&' + y, sorted([k + '=' + v for k, v in re_args.items() if k != 'signature'], lambda x, y: cmp(x, y)))
            else:
                args_one_url = ''

            # args two
            args_two_url = request.data

            my_cal_sign = base_auth_url + args_one_url + args_two_url
            sha1 = hashlib.sha1()
            sha1.update(my_cal_sign.encode('utf-8'))
            sha1.update(secretKey.encode('utf-8'))

            if sha1.hexdigest().upper() != sign:
                return error_respond(msg='invalid signature', http_code=403)

            return fun(*args, **kw)

        return wrapper
    return decorator
