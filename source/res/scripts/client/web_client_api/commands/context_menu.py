# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/context_menu.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_ContextMenuCommand = namedtuple('_ContextMenuCommand', ('menu_type', 'custom_parameters'))
_ContextMenuCommand.__new__.__defaults__ = (None, {})
_ContextMenuCommandScheme = {'required': (('menu_type', basestring),)}
_UserContextMenuCommand = namedtuple('_UserContextMenuCommand', ('spa_id', 'user_name', 'custom_items', 'excluded_items'))
_UserContextMenuCommand.__new__.__defaults__ = (None,
 None,
 [],
 [])
_UserContextMenuCommandScheme = {'required': (('spa_id', (int, long, basestring)), ('user_name', basestring)),
 'optional': (('custom_items', list), ('excluded_items', list))}

class ContextMenuCommand(_ContextMenuCommand, SchemeValidator):
    """
    Represents web command for context menu.
    """

    def __init__(self, *args, **kwargs):
        super(ContextMenuCommand, self).__init__(_ContextMenuCommandScheme)


class UserContextMenuCommand(_UserContextMenuCommand, SchemeValidator):
    """
    Represents user's context menu command.
    """

    def __init__(self, *args, **kwargs):
        super(UserContextMenuCommand, self).__init__(_UserContextMenuCommandScheme)


def createContextMenuHandler(handlerFunc):
    data = {'name': 'context_menu',
     'cls': ContextMenuCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
