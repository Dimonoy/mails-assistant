import logging as _logging

_logging.basicConfig(
    level=_logging.WARNING,
    style='{',
    format='[{module} - {levelname}]: {message}',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = _logging.getLogger('mails-assistant')
logger.setLevel(_logging.DEBUG)
