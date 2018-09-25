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



import os
from xml.parsers.expat import ParserCreate


class ParseTokenConfig(object):

    class HeadersSaxHandler(object):
        def __init__(self):
            self.users = {}
            self.current_user_token = ''
            self.current_tag = ''
            self.user_child_tags = ['x-auth-token', 'Installation-ID', 'client', 'broker_id']

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

    def __init__(self):
        self.handler = self.HeadersSaxHandler()
        self.parser = ParserCreate()
        self.parser.returns_unicode = True
        self.parser.StartElementHandler = self.handler.start_element
        self.parser.EndElementHandler = self.handler.end_element
        self.parser.CharacterDataHandler = self.handler.char_data
        self.xml_path = reduce(lambda x,y: os.path.join(x, y), ['config_file', 'xml', 'token_config.xml'])
        self.f = None


    def get_config(self):
        self.f = open(self.xml_path, 'r')
        self.parser.ParseFile(self.f)
        return self.handler.users


    def __del__(self):
        if not self.f.closed:
            self.f.close()
