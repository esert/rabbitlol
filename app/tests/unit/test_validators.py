import pytest

from app.validators import (
    ParamException,
    validate_default_url,
    validate_description,
    validate_name,
    validate_url_pattern,
)


def test_validators():
    with pytest.raises(ParamException):
        validate_name(None)
    with pytest.raises(ParamException):
        validate_name('')
    with pytest.raises(ParamException):
        validate_name('a' * 65)
    with pytest.raises(ParamException):
        validate_name('hello world' * 65)
    validate_name('h')
    assert 'a' * 64 == validate_name(' ' + 'a' * 64 + ' ')

    with pytest.raises(ParamException):
        validate_description('a' * 257)
    assert 'a' * 256 == validate_description(' ' + 'a' * 256 + ' ')
    validate_description('')
    validate_description(None)

    with pytest.raises(ParamException):
        validate_url_pattern('')
    with pytest.raises(ParamException):
        validate_url_pattern(None)
    with pytest.raises(ParamException):
        validate_url_pattern('a' * 2049)
    assert 'a' * 2048 == validate_url_pattern(' ' + 'a' * 2048 + ' ')

    with pytest.raises(ParamException):
        validate_default_url('a' * 2049)
    assert 'a' * 2048 == validate_default_url(' ' + 'a' * 2048 + ' ')
    validate_default_url('')
    validate_default_url(None)
