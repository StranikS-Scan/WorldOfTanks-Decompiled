# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/clan_management.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_ClanManagementCommand = namedtuple('_ClanManagementCommand', ('action', 'custom_parameters'))
_ClanManagementCommand.__new__.__defaults__ = (None, {})
_ClanManagementCommandScheme = {'required': (('action', basestring),)}

class ClanManagementCommand(_ClanManagementCommand, SchemeValidator):
    """
    Represents web command for clan management.
    """

    def __init__(self, *args, **kwargs):
        super(ClanManagementCommand, self).__init__(_ClanManagementCommandScheme)


def createClanManagementHandler(handlerFunc):
    data = {'name': 'clan_management',
     'cls': ClanManagementCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
