# util.py
# aoneill - 01/21/18

from flask import jsonify

def make_response(message, status = 200, **kwargs):
  data = dict([('msg', message), ('error', status != 200)])
  data.update(kwargs)

  resp = jsonify(**data)
  resp.status_code = status
  return resp

