# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/context_menu.py
from command import Field, W2CSchema, createSubCommandsHandler, SubCommand

class ContextMenuSchema(W2CSchema):
    menu_type = Field(required=True, type=basestring)


class UserContextMenuSchema(W2CSchema):
    spa_id = Field(required=True, type=(int, long, basestring))
    user_name = Field(required=True, type=basestring)
    custom_items = Field(type=list, default=[])
    excluded_items = Field(type=list, default=[])


def createContextMenuHandler(userMenuHandler):
    subCommands = {'user_menu': SubCommand(subSchema=UserContextMenuSchema, handler=userMenuHandler)}
    return createSubCommandsHandler('context_menu', ContextMenuSchema, 'menu_type', subCommands)
