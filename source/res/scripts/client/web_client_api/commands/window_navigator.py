# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/window_navigator.py
from command import W2CSchema, Field, createSubCommandsHandler, SubCommand

class OpenWindowSchema(W2CSchema):
    window_id = Field(required=True, type=basestring)


class OpenClanCardSchema(W2CSchema):
    clan_dbid = Field(required=True, type=(int, long))
    clan_abbrev = Field(required=True, type=basestring)


class OpenProfileSchema(W2CSchema):
    database_id = Field(required=True, type=(int, long))
    user_name = Field(required=True, type=basestring)


class OpenBrowserSchema(W2CSchema):
    url = Field(required=True, type=basestring)
    title = Field(required=True, type=basestring)
    width = Field(required=True, type=(int, long))
    height = Field(required=True, type=(int, long))
    is_modal = Field(type=bool, default=False)
    show_refresh = Field(type=bool, default=True)
    show_create_waiting = Field(type=bool, default=False)
    is_solid_border = Field(type=bool, default=False)


def createOpenWindowHandler(profileHandler=None, clanCardHandler=None, clanInvitesHandler=None, clanSearchHandler=None, browserHandler=None):
    subCommands = {'profile_window': SubCommand(subSchema=OpenProfileSchema, handler=profileHandler),
     'clan_card_window': SubCommand(subSchema=OpenClanCardSchema, handler=clanCardHandler),
     'clan_invites_window': SubCommand(handler=clanInvitesHandler),
     'clan_search_window': SubCommand(handler=clanSearchHandler),
     'browser': SubCommand(subSchema=OpenBrowserSchema, handler=browserHandler)}
    return createSubCommandsHandler('open_window', OpenWindowSchema, 'window_id', subCommands)


class CloseWindowSchema(W2CSchema):
    window_id = Field(required=True, type=basestring)


def createCloseWindowHandler(browserHandler):
    subCommands = {'browser': SubCommand(handler=browserHandler)}
    return createSubCommandsHandler('close_window', CloseWindowSchema, 'window_id', subCommands)


class OpenTabSchema(W2CSchema):
    tab_id = Field(required=True, type=basestring)
    selected_id = Field(type=basestring)


def createOpenTabHandler(hangarHandler=None, profileHandler=None):
    subCommands = {'hangar': SubCommand(handler=hangarHandler),
     'profile': SubCommand(handler=profileHandler)}
    return createSubCommandsHandler('open_tab', OpenTabSchema, 'tab_id', subCommands)
