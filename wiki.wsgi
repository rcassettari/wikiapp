#! /usr/bin/python3
import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ubuntu/myflaskapp-master')
from wiki import app as application
application.secret_key = 'anything you wish'
