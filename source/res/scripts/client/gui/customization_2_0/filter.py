# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization_2_0/filter.py
from Event import Event
from constants import IGR_TYPE
from elements.qualifier import QUALIFIER_TYPE
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE

class FILTER_TYPE:
    QUALIFIER = 0
    GROUP = 1
    PURCHASE_TYPE = 2
    SHOW_IN_DOSSIER = 3


QUALIFIER_TYPE_INDEX = (QUALIFIER_TYPE.ALL,
 QUALIFIER_TYPE.COMMANDER,
 QUALIFIER_TYPE.GUNNER,
 QUALIFIER_TYPE.DRIVER,
 QUALIFIER_TYPE.RADIOMAN,
 QUALIFIER_TYPE.LOADER)

class PURCHASE_TYPE:
    PURCHASE = 0
    QUEST = 1
    ACTION = 2
    IGR = 3


class Filter(object):

    def __init__(self, availableGroupNames):
        self.changed = Event()
        self.__currentType = None
        self.__currentSlotIdx = None
        self.__availableGroupNames = availableGroupNames
        self.__currentGroup = 'all_groups'
        self.__showInDossier = True
        self.__purchaseType = PURCHASE_TYPE.PURCHASE
        self.__rules = {FILTER_TYPE.SHOW_IN_DOSSIER: self.__isInDossier,
         FILTER_TYPE.QUALIFIER: self.__hasSelectedBonus,
         FILTER_TYPE.GROUP: self.__isInSelectedGroup,
         FILTER_TYPE.PURCHASE_TYPE: self.__hasPurchaseType}
        self.__selectedBonuses = {QUALIFIER_TYPE.ALL: False,
         QUALIFIER_TYPE.COMMANDER: False,
         QUALIFIER_TYPE.GUNNER: False,
         QUALIFIER_TYPE.DRIVER: False,
         QUALIFIER_TYPE.RADIOMAN: False,
         QUALIFIER_TYPE.LOADER: False}
        return

    def fini(self):
        self.__rules = None
        self.__availableGroupNames = None
        self.__selectedBonuses = None
        return

    @property
    def availableGroupNames(self):
        return self.__availableGroupNames

    @property
    def selectedBonuses(self):
        return self.__selectedBonuses

    def isDefaultFilterSet(self):
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            return self.__purchaseType == PURCHASE_TYPE.PURCHASE
        else:
            return not self.__bonusSelected() and self.__currentGroup == 'all_groups' and self.__purchaseType == PURCHASE_TYPE.PURCHASE

    def setDefaultFilter(self):
        self.__currentGroup = 'all_groups'
        for key in QUALIFIER_TYPE_INDEX:
            self.__selectedBonuses[key] = False

        self.__purchaseType = PURCHASE_TYPE.PURCHASE

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

    def check(self, item, filterExceptions=None):
        """ Check if item should be shown.
        
        :param item: customization item to be checked
        :param filterExceptions: dict with exceptions for each rule (format: FILTER_TYPE: items)
        :return: True if item should be shown, False otherwise.
        """
        for filterType, rule in self.__rules.items():
            if filterExceptions is not None and filterType in filterExceptions:
                excludedIDs = map(lambda item: item.getID(), filterExceptions[filterType])
                if item.getID() in excludedIDs:
                    return True
            if not rule(item):
                return False

        return True

    def set(self, filterGroup, filterGroupValue):
        if filterGroup == FILTER_TYPE.QUALIFIER:
            self.__selectedBonuses[QUALIFIER_TYPE_INDEX[filterGroupValue]] ^= True
        elif filterGroup == FILTER_TYPE.GROUP:
            self.__currentGroup = filterGroupValue
        elif filterGroup == FILTER_TYPE.SHOW_IN_DOSSIER:
            self.__showInDossier = filterGroupValue
        elif filterGroup == FILTER_TYPE.PURCHASE_TYPE:
            self.__purchaseType = filterGroupValue

    def setTypeAndIdx(self, cType, slotIdx):
        self.__currentSlotIdx = slotIdx
        if self.__currentType != cType:
            self.__currentType = cType
            self.setDefaultFilter()

    def apply(self):
        self.changed()

    def __isInDossier(self, item):
        return not item.isInDossier if not self.__showInDossier else True

    def __hasSelectedBonus(self, item):
        if not self.__bonusSelected():
            return True
        return True if item.qualifier.getType() == QUALIFIER_TYPE.CAMOUFLAGE else self.__selectedBonuses[item.qualifier.getType()]

    def __isInSelectedGroup(self, item):
        if self.__currentGroup == 'all_groups':
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
