# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/web_handlers.py
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleNotificationCommand, handleSoundCommand, handleRequestCommand, handleContextMenuCommand
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import g_appLoader
from web_client_api import WebCommandException
from web_client_api.commands import createNotificationHandler, createSoundHandler, createRequestHandler, createContextMenuHandler, createRankedBattlesHandler

def createRankedBattlesWebHandlers():
    handlers = [createNotificationHandler(handleNotificationCommand),
     createSoundHandler(handleSoundCommand),
     createRequestHandler(handleRequestCommand),
     createContextMenuHandler(handleContextMenuCommand),
     createRankedBattlesHandler(handleRankedBattlesCommand)]
    return handlers


def handleRankedBattlesCommand(command, ctx):
    """
    Executes ranked battles specific actions
    """
    if command.action in RANKED_BATTLES_ACTIONS:
        RANKED_BATTLES_ACTIONS[command.action](ctx)
    else:
        raise WebCommandException('Unknown ranked battles action: %s!' % command.action)


def _closeBrowser(ctx):
    app = g_appLoader.getApp()
    if app is not None and app.containerManager is not None:
        browserView = app.containerManager.getView(ViewTypes.LOBBY_SUB, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
        if browserView is not None:
            browserView.onCloseView()
            return
    raise WebCommandException('Unable to find RankedBattlesBrowserView!')
    return


RANKED_BATTLES_ACTIONS = {'close_browser': _closeBrowser}
