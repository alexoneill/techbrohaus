from flask import Flask
from flask import jsonify
from flask import request

import door_controls

def main(host='0.0.0.0', port=13338):
    app = Flask(__name__)

    def mk_msg(message, error = False, status = 200, **kwargs):
        data = {
            'error': error,
            'msg': message,
        }
        data.update(kwargs)

        resp = jsonify(**data)
        resp.status_code = status
        return resp

    @app.route("/open-door/<key>")
    def open_door(key):
        if door_controls.key_valid(key):
            if door_controls.open_door():
                return mk_msg("Opened!")
            return mk_msg("Attempt too soon", True, 403)
        return mk_msg("Invalid key", True, 403)

    @app.route("/close-door/<key>")
    def close_door(key):
        if door_controls.key_valid(key):
            if door_controls.close_door():
                return mk_msg("Opened!")
            return mk_msg("Attempt too soon", True, 403)
        return mk_msg("Invalid key", True, 403)

    @app.route("/test-door/<key>")
    def test_door(key):
        if door_controls.key_valid(key):
            door_controls.test_door()
            return mk_msg("Tested!")
        return mk_msg("Invalid key", True, 403)

    @app.route("/get-key/<passcode>")
    def get_key(passcode):
        args = request.args
        hours_str = args.get('hours', default="0")
        days_str = args.get('days', default="0")
        forever_str = args.get('forever', default="false")
        try:
            hours = int(hours_str)
            days = int(days_str)
            forever = forever_str == "true"
            key = door_controls.add_key(passcode, hours=hours, days=days, forever=forever)
            return mk_msg(key)
        except ValueError:
            return mk_msg("Invalid arg", True, 412)

    @app.route("/clean-keys")
    def clean_keys():
        filtered_keys = door_controls.clean_keys()
        return mk_msg("Removed old keys", keys = list(filtered_keys))

    @app.route("/delete-keys")
    def delete_keys():
        filtered_keys = door_controls.delete_keys(request.args.getlist('key'))
        return mk_msg("Removed keys", keys = list(filtered_keys))

    @app.route("/is-valid/<key>")
    def is_valid(key):
        (msg, error, status) = ("Expired", True, 403)
        if door_controls.key_valid(key):
            (msg, error,status) = ("Valid", False, 200)

        return mk_msg(msg, error = error, status = status)

    @app.route("/get-exp/<key>")
    def valid_until(key):
        res = door_controls.valid_until(key)
        if res is None:
            return mk_msg("Key does not exist", True, 200)
        return mk_msg(res, False, 200)
        
    
    app.run(host, port, threaded = True)

if (__name__ == '__main__'):
    import sys
    main(*sys.argv[1:])
