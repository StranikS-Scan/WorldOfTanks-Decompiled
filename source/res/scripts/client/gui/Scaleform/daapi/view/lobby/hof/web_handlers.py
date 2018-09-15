# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hof/web_handlers.py
from functools import partial
from gui.Scaleform.daapi.view.lobby.clans.web_handlers import OPEN_WINDOW_CLAN_SUB_COMMANDS
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleVehiclesCommand, createOpenWindowCommandHandler, handleSoundCommand, handleRequestCommand, handleContextMenuCommand, handleOpenTabCommand, handleCloseWindowCommand
from web_client_api.commands import createVehiclesHandler, createOpenWindowHandler, createSoundHandler, createRequestHandler, createContextMenuHandler, createOpenTabHandler, createCloseWindowHandler

def createHofWebHandlers():
    handlers = [createVehiclesHandler(handleVehiclesCommand),
     createOpenWindowHandler(createOpenWindowCommandHandler(OPEN_WINDOW_CLAN_SUB_COMMANDS)),
     createSoundHandler(handleSoundCommand),
     createRequestHandler(handleRequestCommand),
     createContextMenuHandler(handleContextMenuCommand),
     createOpenTabHandler(handleOpenTabCommand),
     createCloseWindowHandler(partial(handleCloseWindowCommand, None, isWindow=False))]
    return handlers
