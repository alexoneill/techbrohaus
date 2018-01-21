# intercom.py
# nbiggs - 01/21/18

import contextlib
import datetime
import json
import logging
import os
import random
import string


class Intercom(object):
  DIR = '/var/tmp/techbrohaus/intercom'
  KEYS = 'keys.txt'
  PASS = 'pass.txt'

  # Delay between successive openings of the door (in seconds)
  DELAY = 20

  def __init__(self):
    self.last_door_time = None

    # Prep the filesystem
    os.makedirs(self.DIR, exist_ok=True)
    pass_path = os.path.join(self.DIR, self.PASS)
    if (not os.path.isfile(pass_path)):
      raise Exception('Missing password file: %s' % pass_path)

  def open_door(self):
    now = int(datetime.datetime.now().strftime('%s'))
    if ((self.last_door_time is None) or
        (self.last_door_time + self.DELAY < now)):
      self.last_door_time = now

      # SERIAL_OBJ.write(bytearray([1]))
      logging.info('Door opened')
      return True

    return False

  def test_door(self):
    # SERIAL_OBJ.write(bytearray([2]))
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

