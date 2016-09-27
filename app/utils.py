from binascii import hexlify
from datetime import (
    datetime,
    timedelta,
)
from hashlib import sha512
from os import urandom
from random import getrandbits
from urllib import (
    quote,
    quote_plus,
    unquote,
    urlencode,
)
import json
import re

from flask import (
    Blueprint,
    Flask,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
)

from app.routes import HOME
import app.routes as routes


def before_request():
    session.permanent = True
    if request.method == 'POST':
        user_token = session.get('csrf_token')
        form_token = request.form.get('csrf_token')
        if (user_token == None or
            form_token == None or
            user_token != form_token.decode('utf-8')):
            raise RedirectException(HOME)


def get_csrf_token():
    csrf_token = session.get('csrf_token')
    if csrf_token == None:
        csrf_token = generate_random_bytes(16)
        session['csrf_token'] = csrf_token
    return csrf_token


def set_current_user_key(value):
    if value == None:
        session.pop('user_key', None)
    else:
        session['user_key'] = value


def get_current_user_key():
    return session.get('user_key')


def user_signed_in():
    return get_current_user_key() != None


def assert_user_signed_in(redirect_route=HOME):
    if not user_signed_in():
        raise RedirectException(redirect_route)


def assert_user_signed_out(redirect_route=HOME):
    if user_signed_in():
        raise RedirectException(redirect_route)


class RedirectException(Exception):
    def __init__(self, route):
        self.route = route


def get_params(form):
    return dict(((k, v.encode('utf-8')) for k, v in form.iteritems()))


def render(template_name, **kw_args):
    return render_template(
        template_name,
        routes=routes,
        signed_in=user_signed_in(),
        host=request.host_url,
        **kw_args
    )


def generate_random_bytes(bytes):
    return hexlify(urandom(bytes))


def salt_and_hash(content, salt):
    return hexlify(sha512(content + salt).digest())
