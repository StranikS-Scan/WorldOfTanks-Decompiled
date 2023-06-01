# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/clan_helpers.py
import typing
from constants import ClansConfig
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getClanQuestURL(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.QUEST_URL)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCraftMachineURL(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.CRAFT_MACHINE_URL)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getStrongholdEventEnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.STRONGHOLD_EVENT_ENABLED)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getStrongholdEventUrl(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.STRONGHOLD_EVENT_URL)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getStrongholdEventBattleModeSettings(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.STRONGHOLD_EVENT_BATTLE_MODE, ('', 0))
