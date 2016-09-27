from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
import pytest

from app.commands import Commands
from app.tests.utils import (
    setup_ndb,
    tear_down_ndb,
)
from app.tests.utils.mocks import mock
import app.user as user

class TestUser(object):
    def setup(self):
        setup_ndb(self)


    def tearDown(self):
        tear_down_ndb(self)


    def newUser(self, username, commands=None):
        if commands == None:
            commands = Commands()
        return user.User(username=username, commands=commands).put().urlsafe()


    def testFromUrlSafeKey(self):
        key = self.newUser(username='username')

        assert user.User.fromURLSafeKey(key).username == 'username'


    def testFromUsername(self):
        key = self.newUser(username='username')

        assert user.User.fromUsername('username').username == 'username'
        assert user.User.fromUsername('does_not_exist') == None


    def testGetCurrentUser(self):
        user.get_current_user_key = mock(return_value=None)

        assert user.get_current_user() == None

        key = self.newUser(username='username')
        user.get_current_user_key = mock(return_value=key)

        u = user.get_current_user()
        assert u.username == 'username'


def test_commands_property():
    p = user.CommandsProperty()

    p._validate(Commands())
    with pytest.raises(TypeError):
        p._validate(None)

    s = Commands().toJSON()
    assert s == p._to_base_type(p._from_base_type(s))
