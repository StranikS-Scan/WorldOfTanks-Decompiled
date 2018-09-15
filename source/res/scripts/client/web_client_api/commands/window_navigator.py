# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/window_navigator.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_OpenWindowCommand = namedtuple('_OpenWindowCommand', ('window_id', 'custom_parameters'))
_OpenWindowCommand.__new__.__defaults__ = (None, None)
_OpenWindowCommandScheme = {'required': (('window_id', basestring),)}
_OpenClanCardCommand = namedtuple('_OpenClanCardCommand', ('clan_dbid', 'clan_abbrev'))
_OpenClanCardCommand.__new__.__defaults__ = (None, None)
_OpenClanCardScheme = {'required': (('clan_dbid', (int, long)), ('clan_abbrev', basestring))}
_OpenProfileCommand = namedtuple('_OpenProfileCommand', ('database_id', 'user_name'))
_OpenProfileCommand.__new__.__defaults__ = (None, None)
_OpenProfileScheme = {'required': (('database_id', (int, long)), ('user_name', basestring))}
_OpenBrowserCommand = namedtuple('_OpenBrowserCommand', ('url', 'title', 'is_modal', 'show_refresh', 'show_create_waiting', 'width', 'height', 'is_solid_border'))
_OpenBrowserCommand.__new__.__defaults__ = (None,
 None,
 False,
 True,
 False,
 None,
 None,
 False)
_OpenBrowserScheme = {'required': (('url', basestring),
              ('title', basestring),
              ('width', (int, long)),
              ('height', (int, long))),
 'optional': (('is_modal', bool),
              ('show_refresh', bool),
              ('show_create_waiting', bool),
              ('is_solid_border', bool))}
_CloseWindowCommand = namedtuple('_CloseWindowCommand', ('window_id',))
_CloseWindowCommand.__new__.__defaults__ = (None,)
_CloseWindowCommandScheme = {'required': (('window_id', basestring),)}
_CloseBrowserScheme = {}
_OpenTabCommand = namedtuple('_OpenTabCommand', ('tab_id', 'selected_id'))
_OpenTabCommand.__new__.__defaults__ = (None, None)
_OpenTabCommandScheme = {'required': (('tab_id', basestring),),
 'optional': (('selected_id', basestring),)}

class OpenWindowCommand(_OpenWindowCommand, SchemeValidator):
    """
    Represents web command for opening window by id.
    """

    def __init__(self, *args, **kwargs):
        super(OpenWindowCommand, self).__init__(_OpenWindowCommandScheme)


class OpenClanCardCommand(_OpenClanCardCommand, SchemeValidator):
    """
    Represents web command for opening window by id.
    """

    def __init__(self, *args, **kwargs):
        super(OpenClanCardCommand, self).__init__(_OpenClanCardScheme)


class OpenProfileCommand(_OpenProfileCommand, SchemeValidator):
    """
    Represents web command for opening window by id.
    """

    def __init__(self, *args, **kwargs):
        super(OpenProfileCommand, self).__init__(_OpenProfileScheme)


class OpenBrowserCommand(_OpenBrowserCommand, SchemeValidator):
    """
    Represents web command for opening window by id.
    """

    def __init__(self, *args, **kwargs):
        super(OpenBrowserCommand, self).__init__(_OpenBrowserScheme)


def createOpenWindowHandler(handlerFunc):
    data = {'name': 'open_window',
     'cls': OpenWindowCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)


class CloseWindowCommand(_CloseWindowCommand, SchemeValidator):
    """
    Represents web command for closing window by id.
    """

    def __init__(self, *args, **kwargs):
        super(CloseWindowCommand, self).__init__(_CloseWindowCommandScheme)


def createCloseWindowHandler(handlerFunc):
    data = {'name': 'close_window',
     'cls': CloseWindowCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)


class OpenTabCommand(_OpenTabCommand, SchemeValidator):
    """
    Represents web command for opening tab by id.
    """

    def __init__(self, *args, **kwargs):
        super(OpenTabCommand, self).__init__(_OpenTabCommandScheme)


def createOpenTabHandler(handlerFunc):
    data = {'name': 'open_tab',
     'cls': OpenTabCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
