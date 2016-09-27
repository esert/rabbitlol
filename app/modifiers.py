from app.utils import (
    quote,
    quote_plus,
    unquote,
)


class Modifier(object):
    def __init__(self, name, description, run):
        self.name = name
        self.description = description
        self.run = run


percent_encode = Modifier(
    name='percent_encode',
    description='percent encodes the input',
    run=lambda x: quote(x, safe=''),
)
percent_encode_plus = Modifier(
    name='percent_encode_plus',
    description='percent encodes the input, but converts space to plus',
    run=lambda x: quote_plus(x, safe=''),
)
percent_encode_slash = Modifier(
    name='percent_encode_slash',
    description='percent encodes the input except for the slashes',
    run=lambda x: quote(x, safe='/'),
)
percent_encode_plus_slash = Modifier(
    name='percent_encode_plus_slash',
    description=('percent encodes the input except for the slashes, but '
                 'converts space to plus'),
    run=lambda x: quote_plus(x, safe='/'),
)
percent_decode = Modifier(
    name='percent_decode',
    description='percent decodes the input',
    run=lambda x: unquote(x),
)
upper = Modifier(
    name='upper',
    description='converts the input to upper case (ASCII characters only)',
    run=lambda x: x.upper(),
)
lower = Modifier(
    name='lower',
    description='converts the input to lower case (ASCII characters only)',
    run=lambda x: x.lower(),
)

modifiers = [
    percent_encode,
    percent_encode_plus,
    percent_encode_slash,
    percent_encode_plus_slash,
    percent_decode,
    upper,
    lower,
]
modifiers.sort(key=lambda x: x.name)

modifier_mapping = dict(((m.name, m) for m in modifiers))
