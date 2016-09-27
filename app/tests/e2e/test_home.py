from app.commands import (
    Command,
    Commands,
)
from app.handlers import home
from app.routes import HOME
from app.tests.utils import (
    TestClient,
    get_dummy_command,
    make_dummy_user,
    make_url,
    setup_ndb,
    tear_down_ndb,
    verify_html_response,
    verify_redirect_response,
)
from app.tests.utils.mocks import mock_render


class TestHome(object):
    def setup(self):
        self.tc = TestClient()
        setup_ndb(self)
        home.render = mock_render()


    def tearDown(self):
        tear_down_ndb(self)


    def get(self, path, template=None, contains=None, redirect=None):
        response = self.tc.get(path)
        if template != None:
            assert home.render.mock_calls[0][1][0] == template
        if contains != None:
            verify_html_response(response, contains=contains)
        if redirect != None:
            verify_redirect_response(response, redirect)


    def testNoQuery(self):
        self.get(HOME, template='home.html')


    def testGoodQuery(self):
        path = make_url(HOME, q='g hello')
        location = make_url('https://www.google.com/search', q='hello')
        self.get(path, redirect=location)


    def testGoodDefaultQuery(self):
        path = make_url(HOME, q='hello world', default='g')
        location = make_url('https://www.google.com/search', q='hello world')
        self.get(path, redirect=location)


    def testNonAsciiQuery(self):
        path = make_url(HOME, q='g \xc3\xb4\xc3\xb6\xc3\xb2')
        location = make_url(
            'https://www.google.com/search',
            q='\xc3\xb4\xc3\xb6\xc3\xb2',
        )
        self.get(path, redirect=location)


    def testMalformedQuery(self):
        path = make_url(HOME, q='')
        self.get(path, redirect='http://localhost' + HOME)


    def testBadQuery(self):
        path = make_url(HOME, q='hello world')
        self.get(
            path,
            template='command_error.html',
            contains='Unknown command',
        )


    def testBadDefaultQuery(self):
        path = make_url(HOME, q='hello world', default='bye')
        self.get(
            path,
            template='command_error.html',
            contains='Unknown default command',
        )


    def testGoodQueryWithBadDefault(self):
        path = make_url(HOME, q='g hello', default='bye')
        location = make_url('https://www.google.com/search', q='hello')
        self.get(path, redirect=location)


    def testMissingArguments(self):
        path = make_url(HOME, q='cron *')
        self.get(
            path,
            template='command_error.html',
            contains='Not enough arguments',
        )


    def testSignedInUser(self):
        commands = [
            get_dummy_command(name='a', url_pattern='https://{1}{2}.com'),
        ]
        self.tc.signInUser(make_dummy_user(commands=commands))

        path = make_url(HOME, q='a b c')
        self.get(path, redirect='https://bc.com')

        path = make_url(HOME, q='another query')
        self.get(
            path,
            template='command_error.html',
            contains='Unknown command',
        )
