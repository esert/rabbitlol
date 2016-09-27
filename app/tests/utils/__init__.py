from re import (
    DOTALL,
    match,
)

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

from app import app
from app.commands import (
    Command,
    Commands,
)
from app.user import (
    Key,
    User,
)
from app.utils import quote


def setup_ndb(test):
    test.testbed = testbed.Testbed()
    test.testbed.activate()
    test.testbed.init_datastore_v3_stub()
    test.testbed.init_memcache_stub()
    ndb.get_context().clear_cache()


def tear_down_ndb(test):
    test.testbed.deactivate()


def make_url(path, **kwargs):
    params = ['%s=%s' % (k, quote(v)) for k, v in kwargs.items()]
    params.sort()
    return '%s?%s' % (path, '&'.join(params))


def verify_hex_str(s, n):
    assert isinstance(s, str) and match('^[a-f0-9]{%d}$' % n, s) != None


def verify_html_response(response, contains=None):
    assert response.status_code == 200
    assert response.content_type == 'text/html; charset=utf-8'
    assert match(r'^<!DOCTYPE html>\n<html>.*</html>$', response.data, DOTALL)
    if contains != None:
        assert match(
            '^.*%s.*$' % '.*'.join(contains.split()),
            response.data,
            DOTALL,
        )


def verify_redirect_response(response, location):
    assert response.status_code == 302
    assert response.content_type == 'text/html; charset=utf-8'
    assert response.location == location


class TestClient(object):
    def __init__(self):
        self.user_key = None
        self.csrfToken = None


    def signInUser(self, user):
        self.user_key = user.key.urlsafe()


    def setCSRFToken(self, csrf_token):
        self.csrfToken = csrf_token


    def get(self, *args, **kwargs):
        with app.test_client() as tc:
            with tc.session_transaction() as s:
                if self.user_key != None:
                    s['user_key'] = self.user_key
                if self.csrfToken != None:
                    s['csrf_token'] = self.csrfToken
            return tc.get(*args, **kwargs)


    def post(self, *args, **kwargs):
        with app.test_client() as tc:
            with tc.session_transaction() as s:
                if self.user_key != None:
                    s['user_key'] = self.user_key
                if self.csrfToken != None:
                    s['csrf_token'] = self.csrfToken
            return tc.post(*args, **kwargs)


def make_dummy_user(username='username', commands=None, default_command=None):
    if commands == None:
        commands = []
    user_key = User(
        username=username,
        commands=Commands(commands),
        defaultCommand=default_command,
    ).put()
    return user_key.get()


def get_dummy_command(
        name='example',
        description='description',
        url_pattern='https://www.example.com/{1}',
        default_url='https://www.example.com',
):
    return Command(
        name=name,
        description=description,
        url_pattern=url_pattern,
        default_url=default_url,
    )
