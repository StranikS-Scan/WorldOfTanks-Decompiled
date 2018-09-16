# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/clan_management.py
from command import W2CSchema, Field, createSubCommandsHandler, SubCommand

class ClanManagementSchema(W2CSchema):
    action = Field(required=True, type=basestring)


def createClanManagementHandler(membersOnlineHandler=None, membersStatusHandler=None, friendsStatusHandler=None):
    subCommands = {'members_online': SubCommand(handler=membersOnlineHandler),
     'members_status': SubCommand(handler=membersStatusHandler),
     'friends_status': SubCommand(handler=friendsStatusHandler)}
    return createSubCommandsHandler('clan_management', ClanManagementSchema, 'action', subCommands)
