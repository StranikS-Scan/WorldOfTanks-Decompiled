# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hof/web_handlers.py
from gui.Scaleform.daapi.view.lobby.clans.web_handlers import handleOpenClanCard, handleOpenClanInvites, handleOpenClanSearch
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleGetVehicleInfo, handleSoundCommand, handleRequestWgniToken, handlerRequestGraphicsSettings, handleShowUserContextMenu, getOpenHangarTabHandler, getOpenProfileTabHandler, handleCloseBrowserView, handleRequestAccessToken
from web_client_api.commands import createVehiclesHandler, createOpenWindowHandler, createSoundHandler, createRequestHandler, createContextMenuHandler, createOpenTabHandler, createCloseWindowHandler

def createHofWebHandlers():
    handlers = [createVehiclesHandler(vehicleInfoHandler=handleGetVehicleInfo),
     createOpenWindowHandler(clanCardHandler=handleOpenClanCard, clanInvitesHandler=handleOpenClanInvites, clanSearchHandler=handleOpenClanSearch),
     createSoundHandler(handleSoundCommand),
     createRequestHandler(token1Handler=handleRequestWgniToken, graphicsSettingsHandler=handlerRequestGraphicsSettings, accessTokenHandler=handleRequestAccessToken),
     createContextMenuHandler(userMenuHandler=handleShowUserContextMenu),
     createOpenTabHandler(hangarHandler=getOpenHangarTabHandler(), profileHandler=getOpenProfileTabHandler()),
     createCloseWindowHandler(handleCloseBrowserView)]
    return handlers
