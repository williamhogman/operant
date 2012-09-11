#!/bin/bash
# Bootstraps a development environment
rm -rf .venv
virtualenv --clear --python=python2.7 .venv
source .venv/bin/activate
export PIP_DOWNLOAD_CACHE=".pip-download-cache"
.venv/bin/pip install -r requirements/test-all.txt
