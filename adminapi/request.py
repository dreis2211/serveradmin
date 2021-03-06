import os
import hashlib
import hmac
import time

from adminapi.cmduser import get_auth_token
from adminapi.filters import BaseFilter

try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, Request, HTTPError, URLError

try:
    import simplejson as json
except ImportError:
    import json

BASE_URL = os.environ.get(
    'SERVERADMIN_BASE_URL',
    'https://serveradmin.innogames.de/api'
)


def calc_security_token(auth_token, timestamp, content):
    message = str(timestamp) + ':' + str(content)
    return hmac.new(
        auth_token.encode('utf8'), message.encode('utf8'), hashlib.sha1
    ).hexdigest()


def send_request(endpoint, data, auth_token, timeout=None):
    if not auth_token:
        auth_token = get_auth_token()

    data_json = json.dumps(data, default=json_encode_extra)

    for retry in reversed(range(3)):
        try:
            req = _build_request(endpoint, auth_token, data_json)
            return json.loads(
                urlopen(req, timeout=timeout).read().decode('utf8'))
        except HTTPError as error:
            if error.code not in (500, 502):
                raise
            if retry == 0:
                raise
        except URLError:
            if retry == 0:
                raise

        # In case of an api error, sleep 5 seconds and try again three times
        time.sleep(5)


def _build_request(endpoint, auth_token, data_json):
    timestamp = int(time.time())
    application_id = hashlib.sha1(auth_token.encode('utf8')).hexdigest()
    security_token = calc_security_token(auth_token, timestamp, data_json)
    headers = {
        'Content-Encoding': 'application/x-json',
        'X-Timestamp': str(timestamp),
        'X-Application': application_id,
        'X-SecurityToken': security_token,
    }
    url = BASE_URL + endpoint

    return Request(url, data_json.encode('utf8'), headers)


def json_encode_extra(obj):
    if isinstance(obj, BaseFilter):
        return obj.serialize()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)
