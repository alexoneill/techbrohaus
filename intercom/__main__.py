# __main__.py
# nbiggs - 01/21/18

from flask import Flask
from flask import request
import argparse
import logging
import sys

from src import august
from src import intercom
from src import util


# Web server defaults
HOST = '0.0.0.0'
PORT = 8000

# Logging settings
LOGGING_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_FILE = '/var/tmp/techbrohaus/log.txt'


def parse_args(argparser):
  '''Setup the supplied argument parser and parse the command-line arguments

  Args:
    argparser, argparse.ArgumetParser: A command-line argument parser

  Returns:
    A python object with the flag settings in it
  '''
  # Specify the host
  argparser.add_argument('-s', '--host',
                         help='Host to run the server on',
                         default=HOST)

  # Specify the port
  argparser.add_argument('-p', '--port',
                         help='Port to run the server on',
                         type=int,
                         default=PORT)

  # Disable threading?
  argparser.add_argument('-t', '--threading',
                         help='Flask threading?',
                         default=True, action='store_false')

  # Parse arguments and produce flags
  return argparser.parse_args()


def logging_setup():
  '''Setup the logging interface.'''
  logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)

  # Add a rotating log handler
  os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
  rotating_logger = logging.handlers.RotatingFileHandler(LOG_FILE,
                                                         backupCount=5)
  rotating_logger.setFormatter(logging.Formatter(LOGGING_FORMAT))

  # Register the alternate handlers
  logging.getLogger().addHandler(rotating_logger)


def main(argparser):
  flags = parse_args(argparser)
  app = Flask(__name__)

  door = intercom.Intercom()
  upstairs = august.August()

  @app.route('/open/<key>')
  def open_door(key):
    if door.key_valid(key):
      if door.open_door():
        if upstairs.open_door():
          return util.make_response('Opened!')
      return util.make_response('Attempt too soon', 403)
    return util.make_response('Invalid key', 403)

  @app.route('/test/<key>')
  def test_door(key):
    if door.key_valid(key):
      door.test_door()
      august.test_door()
      return util.make_response('Tested!')

    return util.make_response('Invalid key', 403)

  @app.route('/august/validate/<code>')
  def validate(code):
    if upstairs.validate(code):
      return util.make_response('Validated!')
    return util.make_response('Not validated')

  @app.route('/key/add/<passcode>')
  def get_key(passcode):
    hours_str = request.args.get('hours', default='0')
    days_str = request.args.get('days', default='0')
    forever_str = request.args.get('forever', default='false')

    try:
      hours = int(hours_str)
      days = int(days_str)
      forever = (forever_str == 'true')

      key = door.add_key(passcode, hours, days, forever)
      return util.make_response(key)

    except ValueError:
      return util.make_response('Invalid arg', 412)

  @app.route('/key/clean/<passcode>')
  def clean_keys(passcode):
    try:
      filtered_keys = door.clean_keys(passcode)
      return util.make_response('Removed old keys', keys = list(filtered_keys))
    except ValueError:
      return util.make_response('Invalid arg', 412)

  @app.route('/key/delete/<passcode>')
  def delete_keys(passcode):
    try:
      filtered_keys = door.delete_keys(passcode, request.args.getlist('key'))
      return util.make_response('Removed keys', keys = list(filtered_keys))
    except ValueError:
      return util.make_response('Invalid arg', 412)

  @app.route('/key/valid/<key>')
  def is_valid(key):
    if door.key_valid(key):
      return util.make_response('Valid')

    return util.make_response('Expired', 403)

  @app.route('/key/expiry/<key>')
  def valid_until(key):
    if (door.valid_until(key) is None):
      return util.make_response('Key does not exist', 412)

    return util.make_response(res)

  app.run(flags.host, flags.port, threaded=not flags.threading)
  return 0

if (__name__ == '__main__'):
  argparser = argparse.ArgumentParser()
  sys.exit(main(argparser))
