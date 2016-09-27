from re import match


def validate_name(name):
    if name == None:
        raise ParamException('Command name is missing.')
    name = name.strip()
    if name == '':
        raise ParamException('Command name is empty.')
    if match(r'^[-_!@#$%+a-zA-Z0-9]+$', name) == None:
        raise ParamException('Command name has invalid characters.')
    n = 64
    if len(name) > n:
        raise ParamException(
            'Command name is too long. Limit is %d characters.' % n,
        )
    return name


def validate_description(description):
    if description != None:
        description = description.strip()
        n = 256
        if len(description) > n:
            raise ParamException(
                'Description is too long. Limit is %d characters.' % n,
            )
    return description


def validate_url_pattern(url_pattern):
    if url_pattern == None:
        raise ParamException('URL pattern is missing.')
    url_pattern = url_pattern.strip()
    if url_pattern == '':
        raise ParamException('URL pattern is empty.')
    n = 2048
    if len(url_pattern) > n:
        raise ParamException(
            'URL pattern is too long. Limit is %d characters.' % n,
        )
    return url_pattern


def validate_default_url(default_url):
    if default_url != None:
        default_url = default_url.strip()
        n = 2048
        if len(default_url) > n:
            raise ParamException(
                'Default URL is too long. Limit is %d characters.' % n,
            )
    return default_url


class ParamException(Exception):
    pass
