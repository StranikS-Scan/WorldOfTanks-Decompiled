# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/clan_helpers.py
from constants import ClansConfig
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getClanQuestURL(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.QUEST_URL)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCraftMachineURL(lobbyContext=None):
    return lobbyContext.getServerSettings().getClansConfig().get(ClansConfig.CRAFT_MACHINE_URL)
