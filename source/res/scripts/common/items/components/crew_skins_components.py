# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/crew_skins_components.py
from typing import Dict, List, Optional
import items
import nations
from items.components.crew_skins_constants import CrewSkinType

class CrewSkin(object):
    itemType = CrewSkinType.CREW_SKIN
    __slots__ = ('id', 'tags', 'priceGroup', 'firstNameID', 'lastNameID', 'iconID', 'description', 'nation', 'rarity', 'historical', 'priceGroupTags', 'realms')

    def __init__(self, ID, priceGroup, firstNameID, lastNameID, iconID, description, rarity, tags, historical, realms):
        self.id = ID
        self.priceGroup = priceGroup
        self.tags = tags
        self.firstNameID = firstNameID
        self.lastNameID = lastNameID
        self.iconID = iconID
        self.description = description
        self.nation = None
        self.rarity = rarity
        self.historical = historical
        self.priceGroupTags = frozenset()
        self.realms = realms
        return

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('crewSkin', self.itemType, self.id)


class PriceGroup(object):
    itemType = CrewSkinType.ITEM_GROUP
    __slots__ = ('price', 'notInShop', 'id', 'name', 'tags')

    def __init__(self):
        self.price = (0, 0, 0)
        self.name = None
        self.id = 0
        self.notInShop = False
        self.tags = []
        return

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('crewSkin', self.itemType, self.id)


class CrewSkinsCache(object):
    __slots__ = ('priceGroups', 'priceGroupNames', 'skins', 'priceGroupTags', 'itemToPriceGroup')

    def __init__(self):
        self.priceGroupTags = {}
        self.skins = {}
        self.priceGroups = {}
        self.priceGroupNames = {}
        self.itemToPriceGroup = {}

    def validateCrewSkinNation(self, itemId, nationID):
        item = self.skins.get(itemId, None)
        if item is None:
            return False
        else:
            nation = nations.NAMES[nationID]
            return False if item.nation and item.nation != nation else True
