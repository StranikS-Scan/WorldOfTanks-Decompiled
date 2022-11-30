# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/gift_machine_helper.py
import typing
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from ny_common.GiftMachineConfig import GiftMachineConfig

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYMarketplaceConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearGiftMachineConfig()


def getCoinPrice():
    config = getNYMarketplaceConfig()
    return config.getCoinPrice()
