# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/filter.py
from constants import IGR_TYPE
from gui.customization.shared import CUSTOMIZATION_TYPE, QUALIFIER_TYPE, FILTER_TYPE, QUALIFIER_TYPE_INDEX, DEFAULT_GROUP_VALUE, PURCHASE_TYPE

class Filter(object):

    def __init__(self, events):
        self.__events = events
        self.__currentType = 0
        self.__currentSlotIdx = 0
        self.__availableGroupNames = ()
        self.__currentGroup = DEFAULT_GROUP_VALUE
        self.__showInDossier = True
        self.__purchaseType = PURCHASE_TYPE.PURCHASE
        self.__isGroupFilterEnabled = True
        self.__selectedBonuses = {QUALIFIER_TYPE.ALL: False,
         QUALIFIER_TYPE.COMMANDER: False,
         QUALIFIER_TYPE.GUNNER: False,
         QUALIFIER_TYPE.DRIVER: False,
         QUALIFIER_TYPE.RADIOMAN: False,
         QUALIFIER_TYPE.LOADER: False}

    def init(self):
        self.__events.onDisplayedElementsAndGroupsUpdated += self.__saveAvailableGroups
        self.__events.onSlotSelected += self.__onSlotSelected

    def fini(self):
        self.__events.onSlotSelected -= self.__onSlotSelected
        self.__events.onDisplayedElementsAndGroupsUpdated -= self.__saveAvailableGroups
        self.__resetFilter()

    @property
    def availableGroupNames(self):
        return self.__availableGroupNames

    @property
    def selectedBonuses(self):
        return self.__selectedBonuses

    @property
    def currentType(self):
        return self.__currentType

    @property
    def purchaseType(self):
        return self.__purchaseType

    @property
    def currentSlotIdx(self):
        return self.__currentSlotIdx

    @property
    def currentGroup(self):
        return self.__currentGroup

    def check(self, item, installedInCurrentSlot):
        return self.__isInDossier(item, installedInCurrentSlot) and self.__hasSelectedBonus(item) and self.__isInSelectedGroup(item) and self.__hasPurchaseType(item)

    def isDefaultFilterSet(self):
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            return self.__purchaseType == PURCHASE_TYPE.PURCHASE
        else:
            return not self.__bonusSelected() and self.__currentGroup == DEFAULT_GROUP_VALUE and self.__purchaseType == PURCHASE_TYPE.PURCHASE

    def isGroupFilterEnabled(self):
        return self.__isGroupFilterEnabled

    def toggleGroupFilterEnabled(self):
        self.__isGroupFilterEnabled = not self.__isGroupFilterEnabled

    def set(self, filterGroup, filterGroupValue):
        if filterGroup == FILTER_TYPE.QUALIFIER:
            self.__selectedBonuses[QUALIFIER_TYPE_INDEX[filterGroupValue]] ^= True
        elif filterGroup == FILTER_TYPE.GROUP:
            self.__currentGroup = filterGroupValue
        elif filterGroup == FILTER_TYPE.SHOW_IN_DOSSIER:
            self.__showInDossier = filterGroupValue
        elif filterGroup == FILTER_TYPE.PURCHASE_TYPE:
            self.__purchaseType = filterGroupValue
        self.__events.onFilterUpdated()

    def setDefault(self):
        self.__resetFilter()
        self.__events.onFilterUpdated()

    def __resetFilter(self):
        if self.__currentType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self.__currentGroup = DEFAULT_GROUP_VALUE
        self.__purchaseType = PURCHASE_TYPE.PURCHASE
        self.__isGroupFilterEnabled = True
        for key in QUALIFIER_TYPE_INDEX:
            self.__selectedBonuses[key] = False

    def __onSlotSelected(self, cType, slotIdx, slotData):
        self.__currentSlotIdx = slotIdx
        if self.__currentType != cType:
            self.__currentType = cType
            self.__resetFilter()

    def __saveAvailableGroups(self, displayedElements, displayedGroups):
        self.__availableGroupNames = displayedGroups

    def __isInDossier(self, item, installedInCurrentSlot):
        return not item.isInDossier or installedInCurrentSlot if not self.__showInDossier else True

    def __hasSelectedBonus(self, item):
        if not self.__bonusSelected():
            return True
        return True if item.qualifier.getType() == QUALIFIER_TYPE.CAMOUFLAGE else self.__selectedBonuses[item.qualifier.getType()]

    def __isInSelectedGroup(self, item):
        if self.__currentGroup == DEFAULT_GROUP_VALUE:
            return True
        else:
            return item.getGroup() == self.__currentGroup

    def __bonusSelected(self):
        for key in QUALIFIER_TYPE_INDEX:
            if self.__selectedBonuses[key]:
                return True

        return False

    def __hasPurchaseType(self, item):
        if self.__purchaseType == PURCHASE_TYPE.PURCHASE:
            return item.getIgrType() == IGR_TYPE.NONE and (item.isInDossier or item.isInShop)
        if self.__purchaseType == PURCHASE_TYPE.QUEST:
            return item.isInQuests and not item.isInDossier
        return item.getIgrType() == IGR_TYPE.PREMIUM and (item.isInDossier or item.isInShop) if self.__purchaseType == PURCHASE_TYPE.IGR else None
