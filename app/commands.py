from app.modifiers import (
    modifier_mapping,
    percent_encode,
)
from app.utils import (
    RedirectException,
    json,
    re,
    unquote,
)
from app.validators import (
    ParamException,
    validate_default_url,
    validate_description,
    validate_name,
    validate_url_pattern,
)


arg_regex = re.compile('{(\d+)(:)?(\d+)?([^:{}]*)}')


class Command(object):
    def __init__(
            self,
            name=None,
            description=None,
            url_pattern=None,
            default_url=None,
    ):
        self.name = validate_name(name)
        self.description = validate_description(description)
        self.url_pattern = validate_url_pattern(url_pattern)
        self.default_url = validate_default_url(default_url)


    def toDict(self):
        return dict(
            filter(
                lambda x: x[1] != None and x[1] != '',
                self.__dict__.iteritems(),
            ),
        )


    def __lt__(self, other):
        left = (
            self.name,
            self.description,
            self.url_pattern,
            self.default_url,
        )
        right = (
            other.name,
            other.description,
            other.url_pattern,
            other.default_url,
        )
        return left < right


    def getRedirectUrl(self, args):
        if len(args) == 0:
            if self.default_url != None:
                return self.default_url
            args.append('')

        parts = []
        last_end = 0
        for match in arg_regex.finditer(self.url_pattern):
            first_index_str, colon, second_index_str, all_modifiers = match.groups()
            first_index = int(first_index_str)
            arg = None
            if colon:
                if first_index >= len(args):
                    raise IndexError()
                if second_index_str:
                    second_index = int(second_index_str) + 1
                    if second_index > len(args):
                        raise IndexError()
                    arg = percent_encode.run(
                        ' '.join(args[first_index:second_index]),
                    )
                else:
                    arg = percent_encode.run(
                        ' '.join(args[first_index:]),
                    )
            else:
                arg = percent_encode.run(args[first_index])
            for m in all_modifiers[1:].split('|'):
                m = modifier_mapping.get(m)
                if m == None:
                    continue
                arg = m.run(arg)
            begin, end = match.span()
            parts.append(self.url_pattern[last_end:begin])
            last_end = end
            parts.append(arg)

        parts.append(self.url_pattern[last_end:])
        return ''.join(parts)


    def getArgumentCount(self):
        args = []
        for match in arg_regex.finditer(self.url_pattern):
            first_index_str, _, second_index_str, _ = match.groups()
            args.append(int(first_index_str))
            if second_index_str != None:
                args.append(int(second_index_str))
        if len(args) == 0:
            return 0
        return max(args)


class Commands(object):
    limit = 200


    def __init__(self, commands=None):
        if commands == None:
            commands = []
        self.mapping = dict(((c.name, c) for c in commands))


    @staticmethod
    def fromJSON(json_str):
        return Commands((Command(**d) for d in json.loads(json_str)))


    def toJSON(self):
        return json.dumps(
            map(lambda x: x.toDict(), self.asSortedList()),
            separators=(',', ':'),
        )


    def asSortedList(self):
        return sorted(self.mapping.itervalues())


    def size(self):
        return len(self.mapping)


    def get(self, name):
        return self.mapping.get(name)


    def add(self, command):
        if command.name in self.mapping:
            raise ParamException(
                '"%s" already exists.' % command.name,
            )
        if len(self.mapping) == self.limit:
            raise ParamException(
                'You can\'t have more than %d commands.' % self.limit,
            )
        self.mapping[command.name] = command


    def remove(self, name):
        del self.mapping[name]


    def getRedirectUrl(self, query, default_command=None):
        query_parts = query.split(None, 1)
        if len(query_parts) == 0:
            raise MalformedQueryException()

        args = []
        if len(query_parts) == 2:
            args.append(query_parts[1])
            args.extend(args[0].split())
            args = map(unquote, args)

        command = self.mapping.get(query_parts[0])
        if command == None:
            if default_command == None:
                raise UnknownCommandException(
                    query=query,
                    command=query_parts[0],
                )

            command = self.mapping.get(default_command)
            if command == None:
                raise UnknownDefaultCommandException(
                    query=query,
                    default_command=default_command,
                )

            args = [query]
            args.extend(query.split())

        try:
            return command.getRedirectUrl(args)
        except IndexError:
            raise NotEnoughArgumentsException(
                query=query,
                command=command.name,
                arg_count=command.getArgumentCount(),
            )


class MalformedQueryException(Exception):
    pass


class UnknownCommandException(Exception):
    def __init__(self, query, command):
        self.query = query.decode('utf-8')
        self.command = command.decode('utf-8')


class UnknownDefaultCommandException(Exception):
    def __init__(self, query, default_command):
        self.query = query.decode('utf-8')
        self.defaultCommand = default_command.decode('utf-8')


class NotEnoughArgumentsException(Exception):
    def __init__(self, query, command, arg_count):
        self.query = query.decode('utf-8')
        self.command = command.decode('utf-8')
        self.argCount = arg_count
