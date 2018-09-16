# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/marathon.py
from command import W2CSchema, Field, SubCommand, createSubCommandsHandler

class MarathonSchema(W2CSchema):
    action = Field(required=True, type=basestring)
    ids = Field(type=list)


def createMarathonHandler(getUserTokens=None, getUserQuests=None):
    subCommands = {'get_tokens': SubCommand(handler=getUserTokens),
     'get_quests': SubCommand(handler=getUserQuests)}
    return createSubCommandsHandler('user_data', MarathonSchema, 'action', subCommands)
