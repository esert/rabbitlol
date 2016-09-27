from app.commands import Commands
from app.handlers import commands
from app.routes import (
    COMMANDS,
    DELETE_COMMAND,
    EDIT_COMMAND_ONLY,
    HOME,
    NEW_COMMAND_ONLY,
    PICK_COMMANDS,
    SET_DEFAULT_COMMAND,
)
from app.tests.utils import (
    TestClient,
    get_dummy_command,
    make_dummy_user,
    setup_ndb,
    tear_down_ndb,
    verify_html_response,
    verify_redirect_response,
)
from app.tests.utils.mocks import (
    mock,
    mock_render,
)


class TestCommands(object):
    def setup(self):
        self.tc = TestClient()
        setup_ndb(self)
        commands.render = mock_render()


    def tearDown(self):
        tear_down_ndb(self)
        self.user = None


    def signInUser(self, commands=None, default_command=None):
        if commands == None:
            commands = [
                get_dummy_command(name='a', url_pattern='https://{1}{2}.com'),
            ]
        self.user = make_dummy_user(commands=commands, default_command=None)
        self.user.put = mock()
        self.tc.signInUser(self.user)


    def setCSRFToken(self, csrf_token):
        self.csrfToken = csrf_token
        self.tc.setCSRFToken(self.csrfToken)


    def verify(
            self,
            response,
            template=None,
            render_args=None,
            contains=None,
            redirect=None,
    ):
        if template != None:
            assert commands.render.mock_calls[0][1][0] == template
        if render_args != None:
            for render_arg in render_args:
                assert render_arg in commands.render.mock_calls[0][2]
        if contains != None:
            verify_html_response(response, contains=contains)
        if redirect != None:
            verify_redirect_response(response, 'http://localhost' + redirect)


    def get(self, path, **kwargs):
        response = self.tc.get(path)
        self.verify(response, **kwargs)


    def post(self, path, data=None, **kwargs):
        response = self.tc.post(path, data=data)
        self.verify(response, **kwargs)


    def testCommandsSignedOut(self):
        self.get(
            COMMANDS,
            template='builtin_commands.html',
            render_args=['builtin_command_groups'],
        )

    def testCommandsSignedIn(self):
        self.signInUser()
        self.get(
            COMMANDS,
            template='commands.html',
            render_args=['commands', 'csrf_token'],
        )


    def testCommandsSignedInEmpty(self):
        self.signInUser(commands=[])
        self.get(
            COMMANDS,
            template='commands.html',
            render_args=['commands', 'csrf_token'],
        )


    def testPickCommandsSignedOut(self):
        self.get(PICK_COMMANDS, redirect=HOME)


    def testPickCommandsSignedInNotEmpty(self):
        self.signInUser()
        self.get(
            PICK_COMMANDS,
            template='pick_commands.html',
            render_args=[
                'builtin_command_groups',
                'checkbox_prefix',
                'csrf_token',
            ],
        )


    def testPickCommandsSignedInEmpty(self):
        self.signInUser([])
        self.get(
            PICK_COMMANDS,
            template='pick_commands.html',
            render_args=[
                'builtin_command_groups',
                'checkbox_prefix',
                'csrf_token',
            ],
        )


    def testPickCommandsSignedInEmptyPostNoArgs(self):
        self.signInUser([])
        self.setCSRFToken('token')
        previous_size = self.user.commands.size()
        self.post(
            PICK_COMMANDS,
            data={
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        assert previous_size == self.user.commands.size()


    def testPickCommandsSignedInEmptyPost(self):
        self.signInUser([])
        self.setCSRFToken('token')
        self.post(
            PICK_COMMANDS,
            data={
                'checkbox_g': True,
                'checkbox_b': True,
                'checkbox_whatever': True,
                'd': True,
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.commands.size() == 2
        assert self.user.commands.get('g') != None
        assert self.user.commands.get('b') != None


    def testPickCommandsSignedInNotEmptyPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        self.post(
            PICK_COMMANDS,
            data={
                'checkbox_g': True,
                'checkbox_b': True,
                'checkbox_whatever': True,
                'd': True,
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.commands.size() == 3
        assert self.user.commands.get('a') != None
        assert self.user.commands.get('g') != None
        assert self.user.commands.get('b') != None


    def testPickCommandsSignedInNotEmptyBadPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        self.post(
            PICK_COMMANDS,
            data={
                'checkbox_a': True,
                'checkbox_g': True,
                'checkbox_b': True,
                'checkbox_whatever': True,
                'd': True,
                'csrf_token': self.csrfToken,
            },
            template='pick_commands.html',
            render_args=[
                'builtin_command_groups',
                'checkbox_prefix',
                'checked',
                'csrf_token',
                'error',
            ],
        )
        self.user.put.assert_not_called()
        assert self.user.commands.size() == 1


    def testEditCommandSignedOut(self):
        self.get(EDIT_COMMAND_ONLY + 'a', redirect=HOME)


    def testEditCommandsSignedInNoCommand(self):
        self.signInUser()
        self.get(EDIT_COMMAND_ONLY, redirect=NEW_COMMAND_ONLY)


    def testEditCommandsSignedInBadCommand(self):
        self.signInUser()
        self.get(EDIT_COMMAND_ONLY + 'b', redirect=NEW_COMMAND_ONLY + 'b')


    def testEditCommandsSignedIn(self):
        self.signInUser()
        command = self.user.commands.get('a')
        self.get(
            EDIT_COMMAND_ONLY + command.name,
            template='new_command.html',
            render_args=[
                'action',
                'csrf_token',
                'default_url',
                'description',
                'name',
                'original_command',
                'url_pattern',
            ],
            contains=command.name,
        )

    def testEditCommandsSignedInBadPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        c = self.user.commands.get('a')
        self.post(
            EDIT_COMMAND_ONLY + c.name,
            data={
                'name': '',
                'description': c.description or '',
                'url_pattern': c.url_pattern or '',
                'default_url': c.default_url or '',
                'csrf_token': self.csrfToken,
            },
            template='new_command.html',
            render_args=[
                'action',
                'csrf_token',
                'original_command',
                'name',
                'description',
                'url_pattern',
                'default_url',
                'error',
            ],
        )
        self.user.put.assert_not_called()


    def testEditCommandsSignedInGoodPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        c = self.user.commands.get('a')
        self.post(
            EDIT_COMMAND_ONLY + c.name,
            data={
                'name': 'b',
                'description': c.description or '',
                'url_pattern': c.url_pattern or '',
                'default_url': c.default_url or '',
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        new_c = self.user.commands.get('b')
        assert (new_c.name == 'b' and
                new_c.description == c.description and
                new_c.url_pattern == c.url_pattern and
                new_c.default_url == c.default_url), (new_c.default_url, c.default_url)


    def testNewCommandSignedOut(self):
        self.get(NEW_COMMAND_ONLY + 'a', redirect=HOME)


    def testNewCommandsSignedInNoCommand(self):
        self.signInUser()
        self.get(
            NEW_COMMAND_ONLY,
            template='new_command.html',
            render_args=['action', 'csrf_token'],
        )


    def testNewCommandsSignedInExistingCommand(self):
        self.signInUser()
        self.get(NEW_COMMAND_ONLY + 'a', redirect=EDIT_COMMAND_ONLY + 'a')


    def testNewCommandsSignedInNewCommand(self):
        self.signInUser()
        self.get(
            NEW_COMMAND_ONLY + 'b',
            template='new_command.html',
            render_args=['action', 'csrf_token', 'name'],
        )

    def testNewCommandsSignedInBadPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        self.post(
            NEW_COMMAND_ONLY + 'b',
            data={
                'name': 'b',
                'description': '',
                'url_pattern': '',
                'default_url': '',
                'csrf_token': self.csrfToken,
            },
            template='new_command.html',
            render_args=[
                'action',
                'csrf_token',
                'name',
                'description',
                'url_pattern',
                'default_url',
                'error',
            ],
        )
        self.user.put.assert_not_called()
        assert self.user.commands.get('b') == None


    def testNewCommandsSignedInGoodPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        c = self.user.commands.get('a')
        self.post(
            NEW_COMMAND_ONLY,
            data={
                'name': 'b',
                'description': c.description or '',
                'url_pattern': c.url_pattern or '',
                'default_url': c.default_url or '',
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.commands.get('a') != None
        new_c = self.user.commands.get('b')
        assert (new_c.name == 'b' and
                new_c.description == c.description and
                new_c.url_pattern == c.url_pattern and
                new_c.default_url == c.default_url)


    def testNewCommandsSignedInGoodPostTooManyCommands(self):
        commands = []
        for i in xrange(Commands.limit):
            commands.append(get_dummy_command(name=str(i)))
        self.signInUser(commands=commands)
        self.setCSRFToken('token')
        c = self.user.commands.get('0')
        self.post(
            NEW_COMMAND_ONLY,
            data={
                'name': 'b',
                'description': c.description or '',
                'url_pattern': c.url_pattern or '',
                'default_url': c.default_url or '',
                'csrf_token': self.csrfToken,
            },
            template='new_command.html',
            render_args=[
                'action',
                'csrf_token',
                'name',
                'description',
                'url_pattern',
                'default_url',
                'error',
            ],
        )
        self.user.put.assert_not_called()
        assert self.user.commands.size() == Commands.limit
        assert self.user.commands.get('b') == None


    def testDeleteCommandSignedOut(self):
        self.post(DELETE_COMMAND, redirect=HOME)


    def testDeleteCommandSignedInBadPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        self.post(
            DELETE_COMMAND,
            data={
                'delete': 'b',
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_not_called()
        assert self.user.commands.get('a') != None


    def testDeleteCommandSignedInGoodPost(self):
        self.signInUser()
        self.setCSRFToken('token')
        self.post(
            DELETE_COMMAND,
            data={
                'delete': 'a',
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.commands.get('a') == None


    def testSetDefaultCommandSignedOut(self):
        self.post(SET_DEFAULT_COMMAND, redirect=HOME)


    def testSetDefaultCommandSignedNewDefault(self):
        self.signInUser()
        self.setCSRFToken('token')
        assert self.user.getDefaultCommand() == None
        self.post(
            SET_DEFAULT_COMMAND,
            data={
                'default_command': 'a',
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.getDefaultCommand() == 'a'


    def testSetDefaultCommandSignedInDelete(self):
        self.signInUser(default_command='a')
        self.setCSRFToken('token')
        self.post(
            SET_DEFAULT_COMMAND,
            data={
                'csrf_token': self.csrfToken,
            },
            redirect=COMMANDS,
        )
        self.user.put.assert_called()
        assert self.user.getDefaultCommand() == None
