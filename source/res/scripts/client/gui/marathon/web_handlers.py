# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/web_handlers.py
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventController
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleRequestWgniToken, handleRequestAccessToken, handleSoundCommand, getOpenHangarTabHandler, getOpenProfileTabHandler
from web_client_api.commands import createRequestHandler, createSoundHandler, createOpenTabHandler
from web_client_api.commands.marathon import createMarathonHandler

def createMarathonWebHandlers():
    handlers = [createSoundHandler(handleSoundCommand),
     createMarathonHandler(getUserTokens=handleGetTokens, getUserQuests=handleGetQuests),
     createRequestHandler(token1Handler=handleRequestWgniToken, accessTokenHandler=handleRequestAccessToken),
     createOpenTabHandler(hangarHandler=getOpenHangarTabHandler(), profileHandler=getOpenProfileTabHandler())]
    return handlers


def handleGetTokens(command, ctx):
    ctrl = dependency.instance(IMarathonEventController)
    tokens = ctrl.getTokensData()
    if hasattr(command, 'ids') and command.ids:
        tokens = {k:v for k, v in tokens.iteritems() if k in command.ids}
    ctx['callback']({'token_list': tokens,
     'action': 'get_tokens'})


def handleGetQuests(command, ctx):
    ctrl = dependency.instance(IMarathonEventController)
    quests = ctrl.getQuestsData()
    if hasattr(command, 'ids') and command.ids:
        quests = {k:v for k, v in quests.iteritems() if k in command.ids}
    ctx['callback']({'quest_list': quests,
     'action': 'get_quests'})
