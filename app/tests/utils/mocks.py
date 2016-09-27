from datetime import datetime

from mock import (
    MagicMock as mock,
    call,
)

from app.utils import render


def mock_datetime(now=None):
    if not isinstance(now, datetime):
        now = datetime.now()
    dt = mock()
    dt.now = mock(return_value=now)
    return dt


def mock_response():
    response = mock()
    response.set_cookie = mock()
    return response


def mock_request(cookies=None, args=None):
    request = mock()
    if cookies == None:
        cookies = {}
    request.cookies = cookies
    if args == None:
        args = {}
    request.args = args
    return request


def mock_render():
    return mock(side_effect=render)


def mock_unicode_string(s):
    unicode_string = mock()
    unicode_string.encode = mock(return_value=s)
    return unicode_string
