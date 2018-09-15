# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/request.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_RequestCommand = namedtuple('_RequestCommand', ('request_id', 'custom_parameters'))
_RequestCommand.__new__.__defaults__ = (None, None)
_RequestCommandScheme = {'required': (('request_id', basestring),)}
_RequestAccessTokenCommand = namedtuple('_RequestAccessTokenCommand', ('force',))
_RequestAccessTokenCommand.__new__.__defaults__ = (False,)
_RequestAccessTokenCommandScheme = {'optional': (('force', bool),)}

class RequestCommand(_RequestCommand, SchemeValidator):
    """
    Represents web command for general purpose requests (eg. Token1 and other common data).
    If there is a need to do some module-specific requests (eg. ClanManagement) then another command should be created.
    """

    def __init__(self, *args, **kwargs):
        super(RequestCommand, self).__init__(_RequestCommandScheme)


class RequestAccessTokenCommand(_RequestAccessTokenCommand, SchemeValidator):

    def __init__(self, *args, **kwargs):
        super(RequestAccessTokenCommand, self).__init__(_RequestAccessTokenCommandScheme)


def createRequestHandler(handlerFunc):
    data = {'name': 'request',
     'cls': RequestCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
