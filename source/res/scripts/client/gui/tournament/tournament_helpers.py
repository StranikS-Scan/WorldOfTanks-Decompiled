# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/tournament/tournament_helpers.py
import typing
from constants import TOURNAMENT_CONFIG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getUniqueViewName
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
    from helpers.server_settings import _TournamentSettings
    from gui.Scaleform.daapi.view.lobby import BrowserView

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getTournamentsConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().tournament


def isTournamentEnabled():
    return getTournamentsConfig().isTournamentEnabled


def showTournaments(url=None):
    from gui.Scaleform.daapi.view.lobby.strongholds.web_handlers import createStrongholdsWebHandlers
    alias = VIEW_ALIAS.LOBBY_TOURNAMENTS
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'url': url or getIgbHost(),
     'webHandlers': createStrongholdsWebHandlers(),
     'returnAlias': VIEW_ALIAS.LOBBY_HANGAR,
     'onServerSettingsChange': _serverSettingChanged}), EVENT_BUS_SCOPE.LOBBY)


def _serverSettingChanged(browser, diff):
    if TOURNAMENT_CONFIG not in diff:
        return
    if not getTournamentsConfig().isTournamentEnabled:
        browser.onCloseView()


def getIgbHost():
    return getTournamentsConfig().igbHostUrl
