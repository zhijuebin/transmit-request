#!/usr/bin/env bash

virtualenv virtual_python
source virtual_python/bin/activate
pip install -r requirements/dev.txt
