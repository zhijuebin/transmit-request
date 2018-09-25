# coding=utf-8
from flask import Flask
from flask_cors import CORS
import config


app = Flask(__name__)
app.config.from_object(config.CurrentConfig)
CORS(app, supports_credentials=True)

from web_app import utils as _
logger = _.get_logger('Main')

from web_app.api import api

app.register_blueprint(api, url_prefix='/api/transmit')
