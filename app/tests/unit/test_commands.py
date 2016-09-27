import pytest

from app.commands import (
    Command,
    Commands,
    MalformedQueryException,
    NotEnoughArgumentsException,
    UnknownCommandException,
    UnknownDefaultCommandException,
)
from app.builtin_commands import (
    builtin_command_groups,
    builtin_commands,
    get_sample_queries,
    sample_queries,
)
from app.validators import (
    ParamException,
    validate_default_url,
    validate_description,
    validate_name,
    validate_url_pattern,
)
from app.utils import (
    RedirectException,
    json,
)


def get_dummy_command(
        name='name',
        description='description',
        url_pattern='url_pattern',
        default_url='default_url',
):
    return Command(
        name=name,
        description=description,
        url_pattern=url_pattern,
        default_url=default_url,
    )


def test_command():
    assert get_dummy_command()

    c = get_dummy_command(url_pattern='pattern', default_url=None)
    assert c.getRedirectUrl([]) == 'pattern'
    assert c.getRedirectUrl(['a']) == 'pattern'

    c = get_dummy_command(url_pattern='pattern', default_url='default')
    assert c.getRedirectUrl([]) == 'default'
    assert c.getRedirectUrl(['a']) == 'pattern'

    c = get_dummy_command(url_pattern='pattern-{0}', default_url=None)
    assert c.getRedirectUrl([]) == 'pattern-'
    assert c.getRedirectUrl(['a']) == 'pattern-a'
    assert c.getRedirectUrl(['a b', 'a', 'b']) == 'pattern-a%20b'

    c = get_dummy_command(url_pattern='pattern-{0}{3}{1}', default_url=None)
    with pytest.raises(IndexError):
        c.getRedirectUrl(['ab', 'a', 'b'])
    assert c.getRedirectUrl(['abc', 'a', 'b', 'c']) == 'pattern-abcca'
    assert c.getRedirectUrl(['abcd', 'a', 'b', 'c', 'd']) == 'pattern-abcdca'

    a = get_dummy_command()
    b = Command(**a.toDict())
    assert not (a < b) and not (b < a)

    a = get_dummy_command(name='a')
    b = get_dummy_command(name='b')
    assert a < b
    assert not a > b

    c = get_dummy_command(url_pattern='pattern')
    assert c.getArgumentCount() == 0

    c = get_dummy_command(url_pattern='{0}')
    assert c.getArgumentCount() == 0

    c = get_dummy_command(url_pattern='{1}pattern{3}')
    assert c.getArgumentCount() == 3

    c = get_dummy_command(url_pattern='{2}pattern')
    assert c.getArgumentCount() == 2


def test_commands():
    commands = Commands()
    assert len(commands.mapping) == 0

    commands = Commands.fromJSON(builtin_commands.toJSON())

    assert len(commands.mapping) == len(builtin_commands.mapping)
    for k, v in commands.mapping.items():
        assert k == v.name
        other = builtin_commands.mapping[k]
        assert not (v < other) and not (other < v)

    assert isinstance(commands.toJSON(), str)
    json.loads(commands.toJSON())

    l = commands.asSortedList()
    assert len(l) == commands.size()
    for c in l:
        other = commands.mapping[c.name]
        assert not (c < other) and not (other < c)

    assert commands.get('g') != None
    assert commands.get('name') == None

    commands.add(get_dummy_command())
    assert commands.get('name') != None

    with pytest.raises(ParamException):
        commands.add(get_dummy_command())

    with pytest.raises(ParamException):
        other_commands = Commands()
        for i in xrange(Commands.limit + 1):
            other_commands.add(get_dummy_command(name=str(i)))

    commands.remove('name')
    assert commands.get('name') == None

    with pytest.raises(MalformedQueryException):
        commands.getRedirectUrl('')
    with pytest.raises(MalformedQueryException):
        commands.getRedirectUrl('     ')
    with pytest.raises(UnknownCommandException):
        commands.getRedirectUrl('unknown_command')
    with pytest.raises(UnknownDefaultCommandException):
        commands.getRedirectUrl('unknown_command', 'unknown_default_command')
    with pytest.raises(NotEnoughArgumentsException):
        commands.getRedirectUrl('cron *')

    g_out = 'https://www.google.com/search?q=hello%20world'
    assert commands.getRedirectUrl('g hello world') == g_out
    assert commands.getRedirectUrl('g hello world', 'b') == g_out

    b_out = 'https://www.bing.com/search?q=hello%20world'
    assert commands.getRedirectUrl('hello world', 'b') == b_out


def test_builtin_commands():
    # builtin commands must be unique
    mapping = dict(builtin_commands.mapping)
    for c in builtin_commands.asSortedList():
        assert c.name == validate_name(c.name)
        assert c.description == validate_description(c.description)
        assert c.url_pattern == validate_url_pattern(c.url_pattern)
        assert c.default_url == validate_default_url(c.default_url)
        mapping.pop(c.name)
    assert len(mapping) == 0
    for c in builtin_commands.mapping.values():
        assert c.url_pattern != c.default_url, c.name
    names = [g.name for g in builtin_command_groups]
    assert len(names) == len(set(names))


def test_sample_queries():
    commands = [s.command for s in sample_queries]
    assert len(commands) == len(set(commands))
    for sample_query in sample_queries:
        assert len(sample_query.query) > 0
        assert len(sample_query.comment) > 0
    shuffled_commands = [s.command for s in get_sample_queries()]
    assert set(commands) == set(shuffled_commands)
    assert len(sample_queries) > 0
