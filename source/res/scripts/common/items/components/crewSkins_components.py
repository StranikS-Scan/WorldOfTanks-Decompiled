# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/crewSkins_components.py
import items
import nations
from constants import CURRENT_REALM, CURRENT_REALM_IS_REGIONAL
from items import ITEM_TYPES
from items.components.crewSkins_constants import CrewSkinType, TANKMAN_SEX, CREW_SKIN_PROPERTIES_MASKS
from soft_exception import SoftException

class CrewSkin(object):
    itemType = CrewSkinType.CREW_SKIN
    __slots__ = ('id', 'tags', 'priceGroup', 'firstNameID', 'lastNameID', 'iconID', 'description', 'roleID', 'nation', 'sex', 'rarity', 'maxCount', 'historical', 'soundSetID', 'priceGroupTags', 'realms')

    def __init__(self, ID, priceGroup, firstNameID, lastNameID, iconID, description, rarity, maxCount, tags, historical, soundSetID, realms):
        self.id = ID
        self.priceGroup = priceGroup
        self.tags = tags
        self.firstNameID = firstNameID
        self.lastNameID = lastNameID
        self.iconID = iconID
        self.description = description
        self.roleID = None
        self.sex = ''
        self.nation = None
        self.rarity = rarity
        self.maxCount = maxCount
        self.historical = historical
        self.soundSetID = soundSetID if soundSetID else '-'
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

    def validateCrewSkin(self, tmanDescr, itemId):
        item = self.skins.get(itemId, None)
        return (False, CREW_SKIN_PROPERTIES_MASKS.EMPTY_MASK, '{} not found'.format(itemId)) if item is None else self._validateItem(tmanDescr, item)

    def confirmCrewSkinRole(self, role, itemId):
        item = self.skins.get(itemId, None)
        if item is None:
            return False
        else:
            return False if item.roleID and item.roleID != role else True

    @staticmethod
    def _validateItem(tmanDescr, item):
        resultMask = CREW_SKIN_PROPERTIES_MASKS.EMPTY_MASK
        resultMsg = ''
        if item.roleID and item.roleID != tmanDescr.role:
            resultMask = resultMask | CREW_SKIN_PROPERTIES_MASKS.ROLE
            resultMsg += '{} {} incompatible roles {};'.format(item.roleID, item.id, tmanDescr.role)
        tmanSex = TANKMAN_SEX.getTankmanSex(tmanDescr)
        if item.sex and item.sex != tmanSex:
            resultMask = resultMask | CREW_SKIN_PROPERTIES_MASKS.SEX
            resultMsg += '{} {} incompatible sex {};'.format(item.sex, item.id, tmanSex)
        nation = nations.NAMES[tmanDescr.nationID]
        if item.nation and item.nation != nation:
            resultMask = resultMask | CREW_SKIN_PROPERTIES_MASKS.NATION
            resultMsg += '{} {} incompatible nation {};'.format(item.nation, item.id, nation)
        return (resultMask == 0, resultMask, resultMsg)
