"""Validation of config values."""
from urllib import parse


def integer_0_or_1(value):
    """Validate an integer that should be either 0 or 1."""
    if not isinstance(value, int):
        raise ValueError('"%s" is not a valid value. It must be an integer.' % value)
    if value < 0 or value > 1:
        raise ValueError('%s is not a valid value. It must be set to either 0 or 1.' % value)


def true_or_false(value):
    """Check for booleans."""
    if not isinstance(value, bool):
        raise ValueError('"%s" is not a valid value. It must be a boolean value.' % value)


def validate_url(url, path=False):
    """Check if url is valid."""
    if path:
        _value = parse.urlparse(url).path
    else:
        _value = parse.urlparse(url).netloc
    try:
        if _value:
            return True
        else:
            raise ValueError('Invalid value:', _value)
    except:
        raise ValueError('Invalid value:', _value)
