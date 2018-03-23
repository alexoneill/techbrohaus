# august.py
# aoneill - 03/17/18

from urllib.parse import urljoin
import base64
import contextlib
import datetime
import json
import logging
import os
import random
import requests
import string
import time


class August(object):
  # Filesystem setup
  DIR = '/var/tmp/techbrohaus/august'
  TOKEN = 'access_token.txt'
  AUGUST_USER = 'user.txt'
  AUGUST_PASS = 'pass.txt'

  # August API Headers
  AUGUST_API = 'https://api-production.august.com'
  AUGUST_HEADERS = {
      'x-august-api-key': '7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4',
      'x-kease-api-key': '7cab4bbd-2693-4fc1-b99b-dec0fb20f9d4',
      'Content-Type': 'application/json',
      'Accept-Version': '0.0.1',
      'User-Agent': 'August/Luna-6.3.4 (Android; SDK 23; Nexus One)',
    }
  AUGUST_LOCK_ID = 'lock_id.txt'

  def _headers(self):
    # Make a copy of the headers
    headers = list(self.AUGUST_HEADERS.items())

    # Add the access token if it exists
    token_file = os.path.join(self.DIR, self.TOKEN)
    if os.path.exists(token_file):
      with open(token_file) as f:
        headers.append(('x-august-access-token', f.read().strip()))

    return dict(headers)

  def _parse_access_token(self, req):
    # Parse out the access token
    access_token = req.headers['x-august-access-token']

    # Save the access token
    token_file = os.path.join(self.DIR, self.TOKEN)
    with open(token_file, 'w') as f:
      f.write(access_token)

  def _parse_local_token(self):
    token_file = os.path.join(self.DIR, self.TOKEN)
    with open(token_file) as f:
      # Token stored with JWT, parse out the body
      (_, body, _) = tuple(f.read().split('.'))

      # Body is JSON, parse it
      padded = body + ('=' * (-len(body) % 4))
      data = base64.b64decode(padded).decode("utf-8")
      return json.loads(data)

  def _get(self, path):
    # Make the request
    headers = self._headers()
    req = requests.get(urljoin(self.AUGUST_API, path), headers=headers)

    # Parse the access token, then return the request
    self._parse_access_token(req)
    return req

  def _put(self, path, data):
    # Make the request
    headers = self._headers()
    req = requests.put(urljoin(self.AUGUST_API, path), headers=headers,
                        json=data)

    # Parse the access token, then return the request
    self._parse_access_token(req)
    return req

  def _post(self, path, data):
    # Make the request
    headers = self._headers()
    req = requests.post(urljoin(self.AUGUST_API, path), headers=headers,
                         json=data)

    # Parse the access token, then return the request
    self._parse_access_token(req)
    return req

  def _session(self):
    with open(os.path.join(self.DIR, self.AUGUST_USER)) as u:
      with open(os.path.join(self.DIR, self.AUGUST_PASS)) as p:
        # Check to see if we already did the 2FA flow
        if (self._parse_local_token()['vEmail']):
          # Bail if we did
          return

        # Make the session request
        user = u.read().strip()
        passwd = p.read().strip()
        req = self._post('/session', {
            'installId': '0000000-0000-0000-0000-000000000000',
            'password': passwd,
            'identifier': 'email:' + user,
          })

        # Do the login flow: If the user email isn't validated, do some
        # fun 2FA
        if (not req.json()['vEmail']):
          logging.warning('August requires 2FA. Check your email (%s)!' % user)

          # Send the 2FA email
          req = self._post('/validation/email', {
              'value': user,
            })

  def __init__(self):
    # Prep the filesystem
    os.makedirs(self.DIR, exist_ok=True)
    user_path = os.path.join(self.DIR, self.AUGUST_USER)
    pass_path = os.path.join(self.DIR, self.AUGUST_PASS)
    if (not os.path.isfile(user_path) or not os.path.isfile(pass_path)):
      raise Exception('Missing user/password file: %s, %s' %
          (user_path, pass_path))

    # Start the August session
    self._session()

  def validate(self, code):
    with open(os.path.join(self.DIR, self.AUGUST_USER)) as u:
      # Confirm the email
      req = self._post('/validate/email', {
          'email': u.read().strip(),
          'code': code,
        })

      return ('userId' in req.json())

  def open_door(self):
    with open(os.path.join(self.DIR, self.AUGUST_LOCK_ID)) as l:
      req = self._put('/remoteoperate/' + l.read().strip() + '/unlock', {})
      return (req.status_code == 200)

  def test_door(self):
    with open(os.path.join(self.DIR, self.AUGUST_LOCK_ID)) as l:
      req = self._put('/remoteoperate/' + l.read().strip() + '/status', {})
      return (req.status_code == 200)

