# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/strongholds.py
from command import W2CSchema, createSubCommandsHandler, Field, SubCommand

class StrongholdsBattleSchema(W2CSchema):
    action = Field(required=True, type=basestring)


class StrongholdsJoinBattleSchema(W2CSchema):
    unit_id = Field(required=True, type=(int, long))
    periphery_id = Field(required=True, type=(int, long))


def createStrongholdsBattleHandler(openListHandler=None, battleChosenHandler=None, joinBattleHandler=None):
    subCommands = {'open_list': SubCommand(handler=openListHandler),
     'battle_chosen': SubCommand(handler=battleChosenHandler),
     'join_battle': SubCommand(subSchema=StrongholdsJoinBattleSchema, handler=joinBattleHandler)}
    return createSubCommandsHandler('strongholds_battle', StrongholdsBattleSchema, 'action', subCommands)
