# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_helper.py
import typing
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from ny_common.GeneralConfig import GeneralConfig
    from ny_common.NYDogConfig import NYDogConfig

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYGeneralConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearGeneralConfig()


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYDogConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearDogConfig()
