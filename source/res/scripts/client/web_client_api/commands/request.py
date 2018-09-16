# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/request.py
from command import W2CSchema, createSubCommandsHandler, Field, SubCommand

class RequestSchema(W2CSchema):
    request_id = Field(required=True, type=basestring)


class RequestAccessTokenCommand(W2CSchema):
    force = Field(type=bool)


def createRequestHandler(token1Handler=None, graphicsSettingsHandler=None, accessTokenHandler=None):
    subCommands = {'token1': SubCommand(handler=token1Handler),
     'graphics_settings': SubCommand(handler=graphicsSettingsHandler),
     'access_token': SubCommand(subSchema=RequestAccessTokenCommand, handler=accessTokenHandler)}
    return createSubCommandsHandler('request', RequestSchema, 'request_id', subCommands)
