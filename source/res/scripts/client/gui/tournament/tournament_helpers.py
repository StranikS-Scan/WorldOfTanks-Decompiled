# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/tournament/tournament_helpers.py
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui import GUI_SETTINGS

def getTournamentUrl(urlName=None):
    try:
        return _getTMSHost() + GUI_SETTINGS.tournament.get(urlName or 'testUrl')
    except (AttributeError, TypeError):
        LOG_CURRENT_EXCEPTION()
        return None

    return None


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getTMSHost(lobbyContext=None):
    if lobbyContext is None:
        return
    else:
        try:
            return lobbyContext.getServerSettings().tournament.tmsHostUrl
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            return

        return
