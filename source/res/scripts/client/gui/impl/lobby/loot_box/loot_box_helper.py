# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import typing
from collections import namedtuple
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from lootboxes_common import makeLBKeyTokenID
if typing.TYPE_CHECKING:
    from typing import Optional
BonusInfo = namedtuple('SlotBonusInfo', ['probabilitiesList',
 'bonusProbability',
 'limitIDs',
 'subBonusRawData'])
OneOfBonusInfo = namedtuple('OneOfBonusInfo', ['limitIDs', 'subBonusRawData'])
_AGGREGATE_BONUS_TYPES = {'crewBooks': (CREW_BOOK_RARITY.CREW_COMMON, CREW_BOOK_RARITY.CREW_RARE)}

def aggregateSimilarBonuses(bonuses):
    masterAggregateBonuses = {}
    result = []
    for bonus in bonuses:
        if bonus.getName() in _AGGREGATE_BONUS_TYPES:
            needToAddBonus = True
            item, count = bonus.getItems()[0]
            type = item.descriptor.type
            if type in _AGGREGATE_BONUS_TYPES[bonus.getName()]:
                if type in masterAggregateBonuses:
                    _, masterCount = masterAggregateBonuses[type].getItems()[0]
                    if count != masterCount:
                        result.append(bonus)
                        continue
                needToAddBonus = type not in masterAggregateBonuses
                masterBonus = masterAggregateBonuses.setdefault(type, bonus)
                masterBonus.getValue()[item.intCD] = count
            if needToAddBonus:
                result.append(bonus)
        if bonus.getName() == 'collectionItem':
            if bonus.getCollectionId() not in masterAggregateBonuses:
                result.append(bonus)
                masterAggregateBonuses[bonus.getCollectionId()] = bonus
        result.append(bonus)

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isAllVehiclesObtainedInSlot(slot, itemsCache=None):
    inventoryVehicles = itemsCache.items.inventory.getIventoryVehiclesCDs()
    for bonus in slot['bonuses']:
        if bonus.getName() == 'vehicles':
            if any((i[0].intCD not in inventoryVehicles for i in bonus.getVehicles())):
                return False

    return True


def getLootBoxIDFromToken(token):
    return token.split(':')[1] if token.startswith(LOOTBOX_TOKEN_PREFIX) else None


def getLootBoxKeyIDFromToken(token):
    return token.split(':')[1] if token.startswith(LOOTBOX_KEY_PREFIX) else None


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getKeyByTokenID(tokenID, itemsCache=None, lobbyContext=None):
    from gui.shared.gui_items.loot_box import LootBoxKey
    _, keyID = tokenID.split(':')
    keyID = int(keyID)
    keyConfig = lobbyContext.getServerSettings().getLootBoxKeyConfig().get(keyID, {})
    if keyConfig:
        keyToken = makeLBKeyTokenID(keyID)
        return LootBoxKey(keyToken, itemsCache.items.tokens.getTokenCount(keyToken), keyConfig)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getKeyByID(keyID, itemsCache=None, lobbyContext=None):
    from gui.shared.gui_items.loot_box import LootBoxKey
    keyConfig = lobbyContext.getServerSettings().getLootBoxKeyConfig().get(keyID, {})
    if keyConfig:
        keyToken = makeLBKeyTokenID(keyID)
        return LootBoxKey(keyToken, itemsCache.items.tokens.getTokenCount(keyToken), keyConfig)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def hasInfiniteLootBoxes(itemsCache=None):
    return any((lb.isActiveHiddenCount() for lb in itemsCache.items.tokens.getLootBoxes().values()))
