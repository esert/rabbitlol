from binascii import hexlify
from hashlib import sha512

import pytest

from app.tests.utils import verify_hex_str
from app.tests.utils.mocks import (
    mock,
    mock_unicode_string,
)
import app.routes as routes
import app.utils as utils


class TestUtils(object):
    def setup(self):
        utils.session = {}


    def user_key_exists(self):
        utils.set_current_user_key('user_key')


    def no_user_key(self):
        utils.set_current_user_key(None)


    def test_init_auth(self):
        self.user_key_exists()

        assert utils.get_current_user_key() == 'user_key'
        assert utils.user_signed_in()

        self.no_user_key()

        utils.get_current_user_key() == None
        not utils.user_signed_in()


    def test_assert_user_signed_in(self):
        self.user_key_exists()

        utils.assert_user_signed_in()

        self.no_user_key()

        with pytest.raises(utils.RedirectException):
            utils.assert_user_signed_in()


    def test_assert_user_signed_out(self):
        self.user_key_exists()

        with pytest.raises(utils.RedirectException):
            utils.assert_user_signed_out()

        self.no_user_key()

        utils.assert_user_signed_out()


    def test_redirect_exception(self):
        try:
            raise utils.RedirectException('route')
        except utils.RedirectException as e:
            assert e.route == 'route'


    def test_get_params(self):
        params = {
            'param1': mock_unicode_string('str1'),
            'param2': mock_unicode_string('str2'),
        }

        out = utils.get_params(params)
        assert len(out) == 2
        assert out['param1'] == 'str1'
        assert out['param2'] == 'str2'
        for v in params.values():
            v.encode.assert_called_once_with('utf-8')


    def test_render(self):
        template = 'template'
        arg = 'arg'
        utils.request = mock()
        utils.request.host_url = 'localhost'
        utils.render_template = mock(return_value='OK')
        self.user_key_exists()

        utils.render(template, arg=arg)
        utils.render_template.assert_called_with(
            template,
            signed_in=True,
            routes=routes,
            host='localhost',
            arg=arg,
        )

        self.no_user_key()
        utils.render(template, arg=arg)
        utils.render_template.assert_called_with(
            template,
            signed_in=False,
            routes=routes,
            host='localhost',
            arg=arg,
        )


    def test_generate_random_bytes(self):
        n = 16
        a = utils.generate_random_bytes(n)
        b = utils.generate_random_bytes(n)

        assert len(a) == len(b)
        assert len(a) == n * 2
