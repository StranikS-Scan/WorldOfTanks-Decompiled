# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/web_handlers.py
from gui.shared.event_dispatcher import showProfileWindow, requestProfile
from web_client_api.commands.window_navigator import OpenProfileCommand

def _openProfile(command):
    """
    Opens profile window
    """

    def onDossierReceived(databaseID, userName):
        showProfileWindow(databaseID, userName)

    requestProfile(command.database_id, command.user_name, successCallback=onDossierReceived)


OPEN_WINDOW_PROFILE_SUB_COMMANS = {'profile_window': (OpenProfileCommand, _openProfile)}
