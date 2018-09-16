# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/web_handlers.py
from gui.Scaleform.daapi.view.lobby.clans.web_handlers import handleGetMembersOnline, handleGetMembersStatus, handleGetFriendsStatus
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleNotificationCommand, handleSoundCommand, handleRequestWgniToken, handlerRequestGraphicsSettings, handleShowUserContextMenu, handleRequestAccessToken
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import g_appLoader
from web_client_api import WebCommandException
from web_client_api.commands import createNotificationHandler, createSoundHandler, createRequestHandler, createContextMenuHandler, createRankedBattlesHandler, createClanManagementHandler

def createRankedBattlesWebHandlers():
    handlers = [createNotificationHandler(handleNotificationCommand),
     createSoundHandler(handleSoundCommand),
     createRequestHandler(token1Handler=handleRequestWgniToken, graphicsSettingsHandler=handlerRequestGraphicsSettings, accessTokenHandler=handleRequestAccessToken),
     createContextMenuHandler(handleShowUserContextMenu),
     createRankedBattlesHandler(closeBrowser),
     createClanManagementHandler(membersOnlineHandler=handleGetMembersOnline, membersStatusHandler=handleGetMembersStatus, friendsStatusHandler=handleGetFriendsStatus)]
    return handlers


def closeBrowser(command, ctx):
    app = g_appLoader.getApp()
    if app is not None and app.containerManager is not None:
        browserView = app.containerManager.getView(ViewTypes.LOBBY_SUB, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
        if browserView is not None:
            browserView.onCloseView()
            return
    raise WebCommandException('Unable to find RankedBattlesBrowserView!')
    return
