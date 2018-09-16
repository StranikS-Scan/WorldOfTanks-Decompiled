# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/web_handlers.py
from gui.shared.event_dispatcher import showProfileWindow, requestProfile

def handleOpenProfile(command, ctx):

    def onDossierReceived(databaseID, userName):
        showProfileWindow(databaseID, userName)

    requestProfile(command.database_id, command.user_name, successCallback=onDossierReceived)
