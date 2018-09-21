# coding=utf-8

import os


class Config(object):
    @classmethod
    def get(cls, item, default=None):
        if hasattr(cls, item):
            return cls.__getattribute__(cls, item)
        return default


class DevelopmentConfig(Config):
    # eg: 'This is hard to guess'
    SECRET_KEY = 'This is hard to guess'
    # eg: 60 * 60 * 24 * 15
    TOKEN_EXPIRES_IN = 60 * 60 * 24 * 15
    CSRF_ENABLED = True
    # Backend Name
    BACKEND_NAME = 'transmit_request_dev'
    TRANSMIT_HOST = 'http://test-api.truckerpath.com'
    AUTHENTICATION_TOKEN_DICT = '{"xxx": "r:e4664b676496485698989de72b822e36"}'
    CLIENT = 'web_api/1.0.0'
    INSTALLATION_ID = '4f861616-ea9f-44a1-860d-c533271d3b7f'


RUN_ENV = os.environ.get('RUN_ENV') or 'dev'

config = {
    'dev': DevelopmentConfig
}

CurrentConfig = config[RUN_ENV]
