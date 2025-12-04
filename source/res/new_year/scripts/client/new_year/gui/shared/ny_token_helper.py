# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/ny_token_helper.py
from lootboxes_common import makeLootboxTokenID
from new_year.helpers.server_settings import getNewYearGeneralConfig

def getSmallLootBoxTokenId():
    return getNewYearGeneralConfig().getSmallLootboxID()


def getSmallLootBoxToken():
    tokenId = getSmallLootBoxTokenId()
    return makeLootboxTokenID(tokenId) if tokenId else None
