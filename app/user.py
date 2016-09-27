from google.appengine.ext.ndb import (
    Key,
    Model,
    StringProperty,
    TextProperty,
)

from app.commands import Commands
from app.utils import (
    g,
    get_current_user_key,
)


class CommandsProperty(TextProperty):
    def _validate(self, value):
        if not isinstance(value, Commands):
            raise TypeError('Expected a Commands type, got %s' % repr(value))


    def _to_base_type(self, commands):
        return commands.toJSON()


    def _from_base_type(self, json_str):
        return Commands.fromJSON(json_str)


class User(Model):
    service = StringProperty()
    username = StringProperty()
    commands = CommandsProperty()
    defaultCommand = StringProperty()


    def getDefaultCommand(self):
        if self.commands.get(self.defaultCommand) == None:
            return None
        return self.defaultCommand


    def setDefaultCommand(self, default_command):
        if default_command == None:
            self.defaultCommand = ''
        elif self.commands.get(default_command) != None:
            self.defaultCommand = default_command


    @staticmethod
    def fromURLSafeKey(key):
        user_key = Key(urlsafe=key)
        return user_key.get()


    @staticmethod
    def fromUsername(username):
        return User.query(User.username == username).get()


def get_current_user():
    key = get_current_user_key()
    if key != None:
        return User.fromURLSafeKey(key)
    return None
