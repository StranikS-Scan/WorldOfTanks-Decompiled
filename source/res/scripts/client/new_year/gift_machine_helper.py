# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/gift_machine_helper.py
import typing
from helpers import dependency
from lootboxes_common import makeLootboxTokenID
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from ny_common.GiftMachineConfig import GiftMachineConfig

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYGiftMachineConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearGiftMachineConfig()


def getCoinPrice():
    config = getNYGiftMachineConfig()
    return config.getCoinPrice()


def getCoinToken():
    return makeLootboxTokenID(getCoinID())


def getCoinID():
    return getNYGiftMachineConfig().getCoinID()


def getCoinType():
    return getNYGiftMachineConfig().getCoinType()
