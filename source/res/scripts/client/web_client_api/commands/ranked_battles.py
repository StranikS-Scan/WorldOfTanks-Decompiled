# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/ranked_battles.py
from command import W2CSchema, Field, createSubCommandsHandler, SubCommand

class RankedBattlesSchema(W2CSchema):
    action = Field(required=True, type=basestring)


def createRankedBattlesHandler(closeBrowserHandler):
    subCommands = {'close_browser': SubCommand(handler=closeBrowserHandler)}
    return createSubCommandsHandler('ranked_battles', RankedBattlesSchema, 'action', subCommands)
