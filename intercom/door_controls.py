import random
import string
import time
from datetime import datetime, timedelta
from serial import Serial
import subprocess

KEYS_FILENAME = "DOOR_KEYS.txt"
LOG_FILENAME = "DOOR_LOG.txt"
KEYS_LENGTH = 10
SERIAL_PORT = "/dev/ttyACM0"
FOREVER_STR = "forever"
EXP_DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"
SERIAL_OBJ = Serial(port=SERIAL_PORT)
KEYGEN_PASSCODE = "PANDA_EXP"
LAST_OPEN_ATTEMPT = None
LAST_CLOSE_ATTEMPT = None
OPEN_TIMEOUT = 20

def time_now_str():
    now = datetime.now()
    return "{month}/{day}/{year} @ {hour}:{minute}:{sec}".format(month=now.month, day=now.day,
                                                                 year=now.year,hour=now.hour,
                                                                 minute=now.minute,sec=now.second)

def write_log_str():
    LOG_FILE = open(LOG_FILENAME, "a")
    LOG_FILE.write("Opened door (" + time_now_str() + ")\n")
    LOG_FILE.close()

def open_upstairs_door():
    subprocess.call("/home/pi/workspace/DOOR_UPSTAIRS/unlock.sh")

def close_upstairs_door():
    subprocess.call("/home/pi/workspace/DOOR_UPSTAIRS/lock.sh")
    
def open_door():
    global SERIAL_OBJ
    global LAST_OPEN_ATTEMPT
    now = datetime.now()
    if LAST_OPEN_ATTEMPT is None or (LAST_OPEN_ATTEMPT + timedelta(seconds=OPEN_TIMEOUT) < now):
        LAST_OPEN_ATTEMPT = now
        SERIAL_OBJ.write(bytearray([1]))
        open_upstairs_door()
        write_log_str()
        return True
    return False

def close_door():
    global LAST_CLOSE_ATTEMPT
    now = datetime.now()
    if LAST_CLOSE_ATTEMPT is None or (LAST_CLOSE_ATTEMPT + timedelta(seconds=OPEN_TIMEOUT) < now):
        LAST_CLOSE_ATTEMPT = now
        close_upstairs_door()
        return True
    return False
    

def test_door():
    global SERIAL_OBJ
    SERIAL_OBJ.write(bytearray([2]))
    write_log_str()
    
def add_key(passcode, hours=0, days=0, forever=False):
    if passcode != KEYGEN_PASSCODE:
        raise ValueError()
    key = generate_key(KEYS_LENGTH)
    if forever:
        save_key(key,FOREVER_STR)
        return key
    if hours == 0 and days == 0:
        raise ValueError()
    delt = timedelta(hours=hours, days=days)
    dt = datetime.now() + delt
    save_key(key, dt.strftime(EXP_DATE_FORMAT))
    return key
            
def save_key(key, exp_str):
    KEYS_FILE = open(KEYS_FILENAME, "a")
    KEYS_FILE.write("{key},{exp}\n".format(key=key, exp=exp_str))
    KEYS_FILE.close()

def filter_keys(f):
    KEYS_FILE = open(KEYS_FILENAME)
    clean = ""
    removed = []
    with open(KEYS_FILENAME) as lines:
        for line in lines:
            k, exp_str = line.strip().split(",")
            if f(k,exp_str):
                clean += line
            else:
                removed.append(k)
    KEYS_FILE = open(KEYS_FILENAME, "w")
    KEYS_FILE.write(clean)
    KEYS_FILE.close()
    return removed

def clean_key_help(key, exp_str):
    if exp_str == FOREVER_STR:
        return True
    exp = datetime.strptime(exp_str, EXP_DATE_FORMAT)
    return datetime.now() < exp
        
    
def clean_keys():
    return filter_keys(clean_key_help)

def delete_keys_help(keys):
    return (lambda key,exp_str: not key in keys)

def delete_keys(keys):
    return filter_keys(delete_keys_help(keys))

def get_key_info(key):
    with open(KEYS_FILENAME) as lines:
        for line in lines:
            k,exp_str = line.strip().split(",")
            if (key == k):
                return k,exp_str
    return None

def key_valid(key):
    res = get_key_info(key)
    return not res is None and (res[1] == FOREVER_STR or datetime.now() < datetime.strptime(res[1], EXP_DATE_FORMAT))

def valid_until(key):
    res = get_key_info(key)[1]
    return res

def generate_key(length):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])
