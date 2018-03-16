# intercom.py
# nbiggs - 01/21/18

import RPi.GPIO as GPIO
import contextlib
import datetime
import json
import logging
import os
import random
import string
import time


class Intercom(object):
  DIR = '/var/tmp/techbrohaus/intercom'
  KEYS = 'keys.txt'
  PASS = 'pass.txt'

  # Pins to interact with the intercom
  KEY_PIN = 11
  TALK_PIN = 26

  # Delay between successive openings of the door (in seconds)
  DELAY = 20

  def __init__(self):
    self.last_door_time = None

    # Initialize the pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup((self.KEY_PIN, self.TALK_PIN), GPIO.OUT)
    GPIO.output((self.KEY_PIN, self.TALK_PIN), GPIO.LOW)

    # Prep the filesystem
    os.makedirs(self.DIR, exist_ok=True)
    pass_path = os.path.join(self.DIR, self.PASS)
    if (not os.path.isfile(pass_path)):
      raise Exception('Missing password file: %s' % pass_path)

  def _press_button(self, pin):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(pin, GPIO.LOW)

  def open_door(self):
    now = int(datetime.datetime.now().strftime('%s'))
    if ((self.last_door_time is None) or
        (self.last_door_time + self.DELAY < now)):
      self.last_door_time = now

      # Do the door sequence
      GPIO.output((self.KEY_PIN, self.TALK_PIN), GPIO.LOW)
      self._press_button(self.KEY_PIN)
      self._press_button(self.TALK_PIN)
      self._press_button(self.KEY_PIN)

      # Let the person enter
      time.sleep(7)
      self._press_button(self.TALK_PIN)

      logging.info('Door opened')
      return True

    return False

  def test_door(self):
    # Do the door sequence
    GPIO.output((self.KEY_PIN, self.TALK_PIN), GPIO.LOW)
    self._press_button(self.KEY_PIN)
    time.sleep(5)
    self._press_button(self.KEY_PIN)

    logging.info('Tested door')

  def _get_pass(self):
    with open(os.path.join(self.DIR, self.PASS)) as f:
      return f.read().strip()

  def _generate_key(self, length=10):
    return ''.join([random.choice(string.ascii_letters + string.digits)
                     for _ in range(length)])

  @contextlib.contextmanager
  def _open_keys(self):
    key_path = os.path.join(self.DIR, self.KEYS)
    keys = list()
    if (os.path.isfile(key_path)):
      with open(key_path) as f:
        keys = json.load(f)

    new_keys = list()
    yield (keys, new_keys)

    with open(key_path, 'w+') as f:
      json.dump(new_keys, f)

  def _save_key(self, key, expire, forever):
    with self._open_keys() as (keys, new_keys):
      new_keys.extend(keys)
      key = ({
          'key': key,
          'expire': expire,
          'forever': forever
        })

      new_keys.append(key)
      logging.info('Added key: %r' % key)

  def add_key(self, passcode, hours=0, days=0, forever=False):
    if (((passcode != self._get_pass()) or
        ((hours == 0) and (days == 0) and not forever))):
      raise ValueError()

    # Generate a key
    key = self._generate_key()
    dt = datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)

    self._save_key(key, int(dt.strftime('%s')), forever)
    return key

  def _filter_keys(self, func):
    removed = list()
    with self._open_keys() as (keys, new_keys):
      for key in keys:
        if (func(key)):
          new_keys.append(key)
        else:
          removed.append(key)

    return removed

  def clean_keys(self, passcode):
    if (passcode != self._get_pass()):
      raise ValueError()


    now = int(datetime.datetime.now().strftime('%s'))
    return self._filter_keys(lambda key:
      key['forever'] or (now < key['expire']))

  def delete_keys(self, passcode, key_codes):
    if (passcode != self._get_pass()):
      raise ValueError()

    return self._filter_keys(lambda key: key['key'] not in key_codes)

  def get_key_info(self, key_code):
    with self._open_keys() as (keys, new_keys):
      new_keys.extend(keys)
      for key in keys:
        if (key['key'] == key_code):
          return key

    return None

  def key_valid(self, key_code):
    now = int(datetime.datetime.now().strftime('%s'))
    key = self.get_key_info(key_code)

    return ((key is not None) and (key['forever'] or (now < key['expire'])))

  def valid_until(self, key_code):
    key = self.get_key_info(key_code)
    return key['expire']

