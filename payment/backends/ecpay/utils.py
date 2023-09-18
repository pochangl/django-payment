'''
Created on Jan 12, 2014

@author: pochangl
'''
import datetime
import hashlib
import pytz
import urllib
from .settings import settings

timezone = pytz.timezone('Asia/Taipei')

def format_time(dt: datetime.datetime):
    ts = dt.timestamp()
    dt = datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.utc)
    dt = timezone.normalize(dt)
    return dt.strftime(settings.DateTimeFormat)


def generate_CheckMacValue(dictionary, key, iv):
    process_fields = dictionary

    sorted_fields = sorted(process_fields.items())
    sorted_fields.insert(0, ("HashKey", settings.HashKey))
    sorted_fields.append(("HashIV", settings.HashIV))

    urlencoded_string = ""
    for a, b in sorted_fields:
        if type(b) == datetime.datetime:
            b = format_time(b)
        if urlencoded_string != "":
            urlencoded_string = "%s&%s=%s" % (urlencoded_string, a, b)
        else:
            urlencoded_string = "%s=%s" % (a, b)

    urlencoded_string = urllib.parse.quote_plus(urlencoded_string, '')

    md5_input = urlencoded_string.lower().encode('utf-8')
    hasher = hashlib.sha256()
    hasher.update(md5_input)
    return hasher.hexdigest().upper()


def get_CheckMacValue(fields, field_name="CheckMacValue"):
    process_fields = dict(fields.items())
    process_fields.pop(field_name, None)
    return generate_CheckMacValue(dictionary=process_fields, key=settings.HashKey, iv=settings.HashIV)


def decode_params(params_string):
    params = {}
    for param in params_string.split('&'):
        field_name, value = param.split('=')
        params[field_name] = value
    return params
