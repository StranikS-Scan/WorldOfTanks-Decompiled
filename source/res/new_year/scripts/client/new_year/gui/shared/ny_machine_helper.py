# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/ny_machine_helper.py
from helpers import dependency
from lootboxes_common import makeLootboxTokenID
from new_year.helpers.server_settings import getNewYearMachineConfig
from skeletons.gui.shared import IItemsCache

def isMachineEnabled():
    return getNewYearMachineConfig().isEnabled()


def getMachineLootboxTokenId():
    return getNewYearMachineConfig().getLootboxID()


def getMachineLootboxToken():
    tokenId = getMachineLootboxTokenId()
    return makeLootboxTokenID(tokenId) if tokenId else None


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getMachineKeysCount(itemsCache=None):
    return itemsCache.items.tokens.getTokenCount(getMachineLootboxToken())
