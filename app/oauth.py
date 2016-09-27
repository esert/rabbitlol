from urlparse import parse_qs
import logging

from google.appengine.api.urlfetch import (
    GET,
    POST,
    fetch,
)
import oauth2

from app.routes import OAUTH_CALLBACK_ONLY
from app.secrets import (
    FACEBOOK_APP_ID,
    FACEBOOK_APP_SECRET,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from app.utils import (
    generate_random_bytes,
    json,
    request,
    session,
    urlencode,
)


rabbitlol_url = 'https://www.rabbitlol.com'


class OAuthService(object):
    def __init__(self):
        self.redirectURI = '%s%s%s' % (
            rabbitlol_url,
            OAUTH_CALLBACK_ONLY,
            self.name,
        )


    def getInitiateRedirectURL(self, state):
        params = {
            'client_id': self.clientID,
            'redirect_uri': self.redirectURI,
            'scope': self.scope,
            'state': state,
        }
        for k, v in self.getAdditionalInitiateParams().iteritems():
            params[k] = v
        return '%s?%s' % (self.initiateEndpoint, urlencode(params))


    def getAccessToken(self, state, code):
        data = {
            'client_id': self.clientID,
            'client_secret': self.clientSecret,
            'code': code,
            'redirect_uri': self.redirectURI,
            'state': state,
        }
        for k, v in self.getAdditionalAccessTokenParams().iteritems():
            data[k] = v
        return api_post(
            url=self.accessTokenEndpoint,
            headers=self.getHeaders(),
            data=data,
            field='access_token',
        )


    def getAdditionalInitiateParams(self):
        return {}


    def getAdditionalAccessTokenParams(self):
        return {}


    def getHeaders(self):
        return {}


    def getUserID(self, access_token):
        return None


class FacebookOAuthService(OAuthService):
    name = 'facebook'
    clientID = FACEBOOK_APP_ID
    clientSecret = FACEBOOK_APP_SECRET
    scope = 'public_profile'
    initiateEndpoint = 'https://www.facebook.com/dialog/oauth'
    accessTokenEndpoint = 'https://graph.facebook.com/v2.7/oauth/access_token'


    def getAdditionalInitiateParams(self):
        return {
            'response_type': 'code',
        }


    def getUserID(self, access_token):
        return api_get(
            url='https://graph.facebook.com/v2.7/me',
            params={
                'access_token': access_token,
            },
            field='id',
        )


class GithubOAuthService(OAuthService):
    name = 'github'
    clientID = GITHUB_CLIENT_ID
    clientSecret = GITHUB_CLIENT_SECRET
    scope = ''
    initiateEndpoint = 'https://github.com/login/oauth/authorize'
    accessTokenEndpoint = 'https://github.com/login/oauth/access_token'


    def getAdditionalInitiateParams(self):
        return {
            'allow_signup': 'false',
        }


    def getHeaders(self):
        return {
            'Accept': 'application/json',
        }


    def getUserID(self, access_token):
        return api_get(
            url='https://api.github.com/user',
            params={
                'access_token': access_token,
            },
            field='id',
        )


class GoogleOAuthService(OAuthService):
    name = 'google'
    clientID = GOOGLE_CLIENT_ID
    clientSecret = GOOGLE_CLIENT_SECRET
    scope = 'email'
    initiateEndpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
    accessTokenEndpoint = 'https://www.googleapis.com/oauth2/v4/token'


    def getAdditionalInitiateParams(self):
        return {
            'response_type': 'code',
        }


    def getAdditionalAccessTokenParams(self):
        return {
            'grant_type': 'authorization_code',
        }


    def getUserID(self, access_token):
        return api_get(
            url='https://www.googleapis.com/oauth2/v3/userinfo',
            params={
                'access_token': access_token,
                'alt': 'json',
            },
            field='sub',
        )


class TwitterOAuthService(object):
    name = 'twitter'
    oauthTokenURL = 'https://api.twitter.com/oauth/request_token'
    authURL = 'https://api.twitter.com/oauth/authenticate'
    accessTokenURL = 'https://api.twitter.com/oauth/access_token'


    def __init__(self):
        super(TwitterOAuthService, self).__init__()
        self.consumer = oauth2.Consumer(
            TWITTER_CONSUMER_KEY,
            TWITTER_CONSUMER_SECRET,
        )


    def getInitiateRedirectURL(self, _):
        client = oauth2.Client(self.consumer)
        _, content = client.request(self.oauthTokenURL, 'GET')
        args = parse_qs(content)
        oauth_token = args['oauth_token'][0]
        session['twitter_oauth_token'] = oauth_token
        session['twitter_oauth_token_secret'] = args['oauth_token_secret'][0]
        return '%s?oauth_token=%s' % (self.authURL, oauth_token)


    def getAccessToken(self, oauth_token, oauth_verifier):
        if oauth_token != session.pop('twitter_oauth_token', None):
            return None
        token = oauth2.Token(
            oauth_token,
            session.pop('twitter_oauth_token_secret', None),
        )
        token.set_verifier(oauth_verifier)
        return oauth2.Client(self.consumer, token)


    def getUserID(self, client):
        _, content = client.request(self.accessTokenURL, 'GET')
        return parse_qs(content)['user_id'][0]


oauth_service_list = [
    FacebookOAuthService(),
    GithubOAuthService(),
    GoogleOAuthService(),
    TwitterOAuthService(),
]
oauth_services = dict(
    ((service.name, service) for service in oauth_service_list)
)


def api_get(url, **kwargs):
    return api_helper(url=url, method=GET, **kwargs)


def api_post(url, **kwargs):
    return api_helper(url=url, method=POST, **kwargs)


def api_helper(url, method, params=None, data=None, headers=None, field=None):
    ret = None
    try:
        if params != None:
            url = '%s?%s' % (url, urlencode(params))
        payload = None
        if method == POST and data != None:
            payload = urlencode(data)
        if headers == None:
            headers = {}
        ret = fetch(
            url,
            method=method,
            payload=payload,
            headers=headers,
            validate_certificate=True,
        )
        if ret.status_code == 200:
            content = json.loads(ret.content)
            if field != None:
                return content.get(field)
            return content
        msg = api_error_msg(url, method, ret)
        logging.error('OAuth API non-200 response\n%s' % msg)
    except:
        msg = api_error_msg(url, method, ret)
        logging.exception('OAuth API error\n%s' % msg)
    return None


def api_error_msg(url, method, response):
    parts = [
        'URL: %s' % url,
        'Method: %s' % 'POST' if method == POST else 'GET',
    ]
    if response == None:
        parts.append('No response')
    else:
        parts.append('Status code: %s' % response.status_code)
        parts.append('Content: %s' % response.content)
    return '\n'.join(parts)


def set_oauth_state():
    oauth_state = session['oauth_state'] = generate_random_bytes(16)
    return oauth_state


def verify_oauth_state(state):
    return session.pop('oauth_state', None) == state
