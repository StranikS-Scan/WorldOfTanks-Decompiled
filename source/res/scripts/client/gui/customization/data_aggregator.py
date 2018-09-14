# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/data_aggregator.py
import nations
from constants import IGR_TYPE
from gui.customization.elements import InstalledElement, Emblem, Inscription, Camouflage, Qualifier, CamouflageQualifier
from gui.customization.shared import CUSTOMIZATION_TYPE, SLOT_TYPE, TYPE_NAME, EMBLEM_IGR_GROUP_NAME, ELEMENT_PLACEMENT
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.gui.game_control import IIGRController
from skeletons.gui.server_events import IEventsCache
_ITEM_CLASS = {CUSTOMIZATION_TYPE.EMBLEM: Emblem,
 CUSTOMIZATION_TYPE.INSCRIPTION: Inscription,
 CUSTOMIZATION_TYPE.CAMOUFLAGE: Camouflage}
VEHICLE_CAMOUFLAGE_BONUS = {VEHICLE_CLASS_NAME.LIGHT_TANK: 3,
 VEHICLE_CLASS_NAME.MEDIUM_TANK: 3,
 VEHICLE_CLASS_NAME.HEAVY_TANK: 2,
 VEHICLE_CLASS_NAME.AT_SPG: 4,
 VEHICLE_CLASS_NAME.SPG: 2}
_MAX_HULL_SLOTS = 2
_MAX_TURRET_SLOTS = 2

class DataAggregator(object):
    """
    Class which aggregates customization data for currently selected vehicle.
    """
    _questsCache = dependency.descriptor(IEventsCache)

    def __init__(self, events, dependencies):
        self._events = events
        self.__currentVehicleInventoryID = None
        self.__incompleteQuestItems = None
        self.__inventoryItems = None
        self._currentVehicle = dependencies.g_currentVehicle
        self._itemsCache = dependencies.g_itemsCache
        self._vehiclesCache = dependencies.g_vehiclesCache
        self._activeCamouflage = dependencies.g_tankActiveCamouflage
        self._qualifiersCache = dependencies.g_qualifiersCache
        self._displayIgrItems = False
        return

    def init(self):
        self._events.onQuestsUpdated += self.__saveIncompleteQuestItems
        self._events.onInventoryUpdated += self.__saveInventoryItems
        self._itemsCache.onSyncCompleted += self.__onItemsCacheSynchronized
        self._currentVehicle.onChanged += self._update
        self._questsCache.onSyncCompleted += self._update

    def start(self):
        self._update()

    def fini(self):
        self._questsCache.onSyncCompleted -= self._update
        self._events.onQuestsUpdated -= self.__saveIncompleteQuestItems
        self._events.onInventoryUpdated -= self.__saveInventoryItems
        self._itemsCache.onSyncCompleted -= self.__onItemsCacheSynchronized
        self._currentVehicle.onChanged -= self._update
        self.__currentVehicleInventoryID = None
        self.__incompleteQuestItems = None
        self.__inventoryItems = None
        return

    def createElement(self, itemId, cType, cNationID, isInShop=False, isInDossier=False, isInQuests=False, isReplacedByIGR=False, inventoryItems=None):
        rawElement = self.__getRawElement(cType, cNationID, itemId)
        groups = self.__getGroups(cType, cNationID)
        cls = _ITEM_CLASS[cType]
        if cType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            if rawElement[7] in self._qualifiersCache.qualifiers:
                qualifier = Qualifier(self._qualifiersCache.qualifiers[rawElement[7]])
            else:
                qualifier = CamouflageQualifier('winter', VEHICLE_CAMOUFLAGE_BONUS[self._currentVehicle.item.type])
            group = groups[rawElement[0]]
            readableGroupName = group[1]
            if len(group) == 5:
                allowedNations = None
                allowedVehicles = list(group[3])
                notAllowedVehicles = group[4]
            else:
                allowedNations = group[3]
                allowedVehicles = list(group[4])
                notAllowedVehicles = group[5]
        else:
            groupName = rawElement['groupName']
            igrLessGroupName = groupName[3:] if groupName.startswith('IGR') else groupName
            qualifier = CamouflageQualifier(igrLessGroupName, VEHICLE_CAMOUFLAGE_BONUS[self._currentVehicle.item.type])
            allowedNations = None
            allowedVehicles = list(rawElement['allow'])
            notAllowedVehicles = rawElement['deny']
            readableGroupName = '#vehicle_customization:camouflage/{0}'.format(igrLessGroupName)
        numberOfDays = None
        numberOfItems = None
        if inventoryItems is not None:
            if itemId in inventoryItems[cType] and not isInDossier:
                isInDossier = True
                allowedVehicles += inventoryItems[cType][itemId][4]
                if inventoryItems[cType][itemId][6][0]:
                    numberOfItems = inventoryItems[cType][itemId][6][1]
                else:
                    numberOfDays = inventoryItems[cType][itemId][6][1]
            else:
                numberOfDays = self._getIGRReplacedNumberOfDays(itemId, cType)
        notAllowedNations = None if allowedNations is None else []
        if allowedNations is not None:
            for nationID in nations.INDICES.values():
                if nationID not in allowedNations:
                    notAllowedNations.append(nationID)

        return cls({'itemID': itemId,
         'nationID': nations.NONE_INDEX if cType == CUSTOMIZATION_TYPE.EMBLEM else cNationID,
         'rawElement': rawElement,
         'qualifier': qualifier,
         'isInShop': isInShop,
         'isInDossier': isInDossier,
         'isInQuests': isInQuests,
         'allowedVehicles': allowedVehicles,
         'notAllowedVehicles': notAllowedVehicles,
         'allowedNations': allowedNations,
         'notAllowedNations': notAllowedNations,
         'isReplacedByIGR': isReplacedByIGR,
         'numberOfItems': numberOfItems,
         'numberOfDays': numberOfDays,
         'readableGroupName': readableGroupName,
         'price': self.__getPriceAttributes(cNationID, cType)})

    def getIncompleteQuestItems(self):
        return self.__incompleteQuestItems

    def _update(self):
        isNewVehicle = self.__currentVehicleInventoryID is not None and self.__currentVehicleInventoryID != self._currentVehicle.item.invID
        curVehDescr = self._currentVehicle.item.descriptor
        cNationID = curVehDescr.type.customizationNationID
        rawElementGroups = (self._vehiclesCache.customization(cNationID)['camouflageGroups'], self._vehiclesCache.playerEmblems()[0], self._vehiclesCache.customization(cNationID)['inscriptionGroups'])
        installedRawItems = self._getInstalledRawItems(curVehDescr)
        notMigratedElements = self.__getNotMigratedElements(rawElementGroups, installedRawItems)
        self.__updateTankModelAttributes(curVehDescr, installedRawItems)
        installedElements = self.__getInstalledElements(curVehDescr.hull['emblemSlots'], curVehDescr.turret['emblemSlots'], installedRawItems)
        self.__updateInstalledElements(installedElements, isNewVehicle)
        self.__updateDisplayedElementsAndGroups(rawElementGroups, curVehDescr, cNationID, notMigratedElements, installedElements)
        self.__currentVehicleInventoryID = self._currentVehicle.item.invID
        return

    def _getInstalledRawItems(self, curVehDescr):
        return {'camouflages': list(curVehDescr.camouflages),
         'emblems': list(curVehDescr.playerEmblems),
         'inscriptions': list(curVehDescr.playerInscriptions)}

    def _elementIsInShop(self, criteria, cType, nationID):
        shop = self._itemsCache.items.shop

        def camouflageIsInShop(elementID):
            return elementID not in shop.getCamouflagesHiddens(nationID)

        def emblemGroupIsInShop(groupName):
            return groupName not in shop.getEmblemsGroupHiddens() and groupName != EMBLEM_IGR_GROUP_NAME or self._displayIgrItems and groupName == EMBLEM_IGR_GROUP_NAME

        def inscriptionGroupIsInShop(groupName):
            return groupName not in shop.getInscriptionsGroupHiddens(nationID) and groupName != 'IGR' or self._displayIgrItems and groupName == 'IGR'

        return [lambda elementID: camouflageIsInShop(elementID), lambda groupName: emblemGroupIsInShop(groupName), lambda groupName: inscriptionGroupIsInShop(groupName)][cType](criteria)

    def _elementIsIGRReplaced(self, elementID, cType):
        return False

    def _getIGRReplacedNumberOfDays(self, elementID, cType):
        return None

    def __getPriceAttributes(self, cNationID, cType):
        price = (self._itemsCache.items.shop.camouflageCost, self._itemsCache.items.shop.playerEmblemCost, self._itemsCache.items.shop.playerInscriptionCost)
        priceFactor = (self._itemsCache.items.shop.getCamouflagesPriceFactors(cNationID), self._itemsCache.items.shop.getEmblemsGroupPriceFactors(), self._itemsCache.items.shop.getInscriptionsGroupPriceFactors(cNationID))
        vehiclePriceFactor = (self._itemsCache.items.shop.defaults.getVehCamouflagePriceFactor(self._currentVehicle.item.descriptor.type.compactDescr), self._currentVehicle.item.level, self._currentVehicle.item.level)
        defaultPrice = (self._itemsCache.items.shop.defaults.camouflageCost, self._itemsCache.items.shop.defaults.playerEmblemCost, self._itemsCache.items.shop.defaults.playerInscriptionCost)
        defaultPriceFactor = (self._itemsCache.items.shop.defaults.getCamouflagesPriceFactors(cNationID), self._itemsCache.items.shop.defaults.getEmblemsGroupPriceFactors(), self._itemsCache.items.shop.defaults.getInscriptionsGroupPriceFactors(cNationID))
        defaultVehiclePriceFactor = (self._itemsCache.items.shop.defaults.getVehCamouflagePriceFactor(self._currentVehicle.item.descriptor.type.compactDescr), self._currentVehicle.item.level, self._currentVehicle.item.level)
        return {'actual': {'base': price[cType],
                    'factor': priceFactor[cType],
                    'vehicleFactor': vehiclePriceFactor[cType]},
         'default': {'base': defaultPrice[cType],
                     'factor': defaultPriceFactor[cType],
                     'vehicleFactor': defaultVehiclePriceFactor[cType]}}

    def __getInstalledElements(self, vehicleHullSlots, vehicleTurretSlots, installedRawItems):
        installedHullEmblems = []
        installedTurretEmblems = []
        installedHullInscriptions = []
        installedTurretInscriptions = []
        hullEmblemSlotIdx = 0
        hullInscriptionSlotIdx = 0
        turretEmblemSlotIdx = 0
        turretInscriptionSlotIdx = 0
        for slot in vehicleHullSlots:
            if slot.type == SLOT_TYPE[CUSTOMIZATION_TYPE.EMBLEM]:
                installedHullEmblems.append(installedRawItems['emblems'][hullEmblemSlotIdx])
                hullEmblemSlotIdx += 1
            if slot.type == SLOT_TYPE[CUSTOMIZATION_TYPE.INSCRIPTION]:
                installedHullInscriptions.append(installedRawItems['inscriptions'][hullInscriptionSlotIdx])
                hullInscriptionSlotIdx += 1

        for slot in vehicleTurretSlots:
            if slot.type == SLOT_TYPE[CUSTOMIZATION_TYPE.EMBLEM]:
                installedTurretEmblems.append(installedRawItems['emblems'][_MAX_HULL_SLOTS + turretEmblemSlotIdx])
                turretEmblemSlotIdx += 1
            if slot.type == SLOT_TYPE[CUSTOMIZATION_TYPE.INSCRIPTION]:
                installedTurretInscriptions.append(installedRawItems['inscriptions'][_MAX_TURRET_SLOTS + turretInscriptionSlotIdx])
                turretInscriptionSlotIdx += 1

        installedElements = ([], [], [])
        for installedCamouflage in installedRawItems['camouflages']:
            installedElements[CUSTOMIZATION_TYPE.CAMOUFLAGE].append(InstalledElement(CUSTOMIZATION_TYPE.CAMOUFLAGE, installedCamouflage[0], installedCamouflage[2], installedCamouflage[1], ELEMENT_PLACEMENT.HULL))

        for installedHullEmblem in installedHullEmblems:
            installedElements[CUSTOMIZATION_TYPE.EMBLEM].append(InstalledElement(CUSTOMIZATION_TYPE.EMBLEM, installedHullEmblem[0], installedHullEmblem[2], installedHullEmblem[1], ELEMENT_PLACEMENT.HULL))

        for installedTurretEmblem in installedTurretEmblems:
            installedElements[CUSTOMIZATION_TYPE.EMBLEM].append(InstalledElement(CUSTOMIZATION_TYPE.EMBLEM, installedTurretEmblem[0], installedTurretEmblem[2], installedTurretEmblem[1], ELEMENT_PLACEMENT.TURRET))

        for installedHullInscription in installedHullInscriptions:
            installedElements[CUSTOMIZATION_TYPE.INSCRIPTION].append(InstalledElement(CUSTOMIZATION_TYPE.INSCRIPTION, installedHullInscription[0], installedHullInscription[2], installedHullInscription[1], ELEMENT_PLACEMENT.HULL))

        for installedTurretInscription in installedTurretInscriptions:
            installedElements[CUSTOMIZATION_TYPE.INSCRIPTION].append(InstalledElement(CUSTOMIZATION_TYPE.INSCRIPTION, installedTurretInscription[0], installedTurretInscription[2], installedTurretInscription[1], ELEMENT_PLACEMENT.TURRET))

        return installedElements

    def __updateInstalledElements(self, installedElements, newVehicleSelected):
        self._events.onInstalledElementsUpdated(newVehicleSelected, installedElements)

    def __saveIncompleteQuestItems(self, incompleteQuestItems):
        self.__incompleteQuestItems = incompleteQuestItems

    def __saveInventoryItems(self, inventoryItems):
        self.__inventoryItems = inventoryItems

    def __onItemsCacheSynchronized(self, updateReason, invalidItems):
        if updateReason in (CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.SHOP_RESYNC):
            self._update()

    def __getRawElement(self, cType, nationID, itemID):
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            return self._vehiclesCache.customization(nationID)['camouflages'][itemID]
        if cType == CUSTOMIZATION_TYPE.EMBLEM:
            return self._vehiclesCache.playerEmblems()[1][itemID]
        return self._vehiclesCache.customization(nationID)['inscriptions'][itemID] if cType == CUSTOMIZATION_TYPE.INSCRIPTION else None

    def __getGroups(self, cType, nationID):
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            return self._vehiclesCache.customization(nationID)['camouflageGroups']
        if cType == CUSTOMIZATION_TYPE.EMBLEM:
            return self._vehiclesCache.playerEmblems()[0]
        return self._vehiclesCache.customization(nationID)['inscriptionGroups'] if cType == CUSTOMIZATION_TYPE.INSCRIPTION else None

    def __updateTankModelAttributes(self, curVehDescr, installedRawItems):
        activeCamouflage = self._activeCamouflage.get(curVehDescr.type.compactDescr, 0)
        currentCamouflageID = curVehDescr.camouflages[activeCamouflage][0]
        self._events.onTankModelAttributesUpdated([currentCamouflageID, installedRawItems['emblems'], installedRawItems['inscriptions']])

    def __getAvailableElements(self, curVehDescr, cNationID, notMigratedElements, installedElements):
        inDossier = (self._itemsCache.items.getVehicleDossier(curVehDescr.type.compactDescr).getBlock('camouflages'), self._itemsCache.items.getVehicleDossier(curVehDescr.type.compactDescr).getBlock('emblems'), self._itemsCache.items.getVehicleDossier(curVehDescr.type.compactDescr).getBlock('inscriptions'))
        allElements = ({}, {}, {})
        rawElements = [self._vehiclesCache.customization(cNationID)['camouflages'], self._vehiclesCache.playerEmblems()[1], self._vehiclesCache.customization(cNationID)['inscriptions']]
        for cType in CUSTOMIZATION_TYPE.ALL:
            containerToFill = allElements[cType]
            typedRawElements = rawElements[cType]
            for elementID, rawElement in typedRawElements.iteritems():
                replacedByIGRItem = self._elementIsIGRReplaced(elementID, cType)
                isMigrated = elementID not in notMigratedElements[cType]
                isInQuests = elementID in self.__incompleteQuestItems[cType]
                if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
                    criteria = elementID
                else:
                    criteria = rawElement[0]
                isInShop = self._elementIsInShop(criteria, cType, cNationID)
                for element in installedElements[cType]:
                    if element.elementID == elementID:
                        if not self.__isDefaultElement(elementID, cNationID, cType):
                            isInstalled = True
                            break
                else:
                    isInstalled = False

                isInDossier = elementID in inDossier[cType] or replacedByIGRItem and not rawElement[0] == 'auto' or not isMigrated
                if isInShop or isInQuests or isInDossier or isInstalled or elementID in self.__inventoryItems[cType]:
                    containerToFill[elementID] = self.createElement(elementID, cType, cNationID, isInShop, isInDossier, isInQuests, replacedByIGRItem, self.__inventoryItems)

        return allElements

    def __updateDisplayedElementsAndGroups(self, rawElementGroups, curVehDescr, cNationID, notMigratedElements, installedElements):
        allElements = self.__getAvailableElements(curVehDescr, cNationID, notMigratedElements, installedElements)
        displayedElements = ({}, {}, {})
        displayedGroups = (set(), set(), set())
        for cType in CUSTOMIZATION_TYPE.ALL:
            containerToFill = displayedElements[cType]
            for itemID, availableItem in allElements[cType].iteritems():
                if availableItem.isAllowedForCurrentVehicle(self._currentVehicle):
                    containerToFill[itemID] = availableItem

        for cType in CUSTOMIZATION_TYPE.ALL:
            groups = displayedGroups[cType]
            for itemID, item in displayedElements[cType].iteritems():
                groupName = item.getGroup()
                if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
                    userFriendlyNameKey = 'userString'
                else:
                    userFriendlyNameKey = 1
                groups.add((groupName, rawElementGroups[cType][groupName][userFriendlyNameKey]))

        self._events.onDisplayedElementsAndGroupsUpdated(displayedElements, displayedGroups)

    @staticmethod
    def __getNotMigratedElements(rawElementGroups, installedRawItems):
        """
        Returns elements which are on tank and are permanent but are not in
        dossier. After some server migration it's possible that user will get
        into state when his customization elements are not isInDossier but are
        permanently installed on tank (duration == 0). These customization
        elements should be marked as purchased for gold in carousel. But
        we also have nation embles and they also meet that criteria
        thus we have this method.
        
        :param rawElementGroups: groups obtained from xml-s
        :param installedRawItems: raw installed elements
        :return: list of ids for each customization type
        """
        notMigratedElements = (set([]), set([]), set([]))
        for key in installedRawItems.iterkeys():
            for installedRawItem in installedRawItems[key]:
                installedItemID = installedRawItem[0]
                if installedRawItem[2] == 0 and installedItemID is not None and (TYPE_NAME[key] != CUSTOMIZATION_TYPE.EMBLEM or TYPE_NAME[key] == CUSTOMIZATION_TYPE.EMBLEM) and installedItemID not in rawElementGroups[CUSTOMIZATION_TYPE.EMBLEM]['auto'][0]:
                    notMigratedElements[TYPE_NAME[key]].add(installedItemID)

        return notMigratedElements

    def __isDefaultElement(self, elementID, cNationID, cType):
        """ Check if installed element is default for the vehicle.
        
        There are few customization elements that appear on the vehicle by default
        and shouldn't be visible in the carousel and slots.
        
        :return: True is element is default, False otherwise
        """
        if cType == CUSTOMIZATION_TYPE.EMBLEM:
            return self.__getRawElement(cType, cNationID, elementID)[0] == 'auto'
        else:
            return False


class IgrDataAggregator(DataAggregator):
    igrCtrl = dependency.descriptor(IIGRController)

    def __init__(self, events, externalDependencies):
        DataAggregator.__init__(self, events, externalDependencies)
        self._displayIgrItems = False
        self.__igrReplacedItems = None
        return

    def init(self):
        DataAggregator.init(self)
        self.igrCtrl.onIgrTypeChanged += self.__onIGRTypeChanged

    def fini(self):
        self.igrCtrl.onIgrTypeChanged -= self.__onIGRTypeChanged
        DataAggregator.fini(self)

    def _update(self):
        self._displayIgrItems = self.igrCtrl.getRoomType() == IGR_TYPE.PREMIUM
        self.__igrReplacedItems = [{}, {}, {}]
        DataAggregator._update(self)

    def _getInstalledRawItems(self, curVehDescr):
        installedRawItems = DataAggregator._getInstalledRawItems(self, curVehDescr)
        if self._displayIgrItems:
            igrLayout = self._itemsCache.items.inventory.getIgrCustomizationsLayout()
            vehicleId = self._currentVehicle.item.invID
            igrRoomType = self.igrCtrl.getRoomType()
            igrVehDescr = []
            if vehicleId in igrLayout:
                if igrRoomType in igrLayout[vehicleId]:
                    igrVehDescr = igrLayout[vehicleId][igrRoomType]
            for key in igrVehDescr:
                for index in igrVehDescr[key]:
                    replacedItemID = installedRawItems[key][index][0]
                    replacedItemDaysLeft = installedRawItems[key][index][2]
                    replacedItemDaysLeft = replacedItemDaysLeft or None
                    if replacedItemID is not None:
                        self.__igrReplacedItems[TYPE_NAME[key]][replacedItemID] = replacedItemDaysLeft
                    installedRawItems[key][index] = igrVehDescr[key][index]

        return installedRawItems

    def _elementIsIGRReplaced(self, elementID, cType):
        return elementID in self.__igrReplacedItems[cType]

    def _getIGRReplacedNumberOfDays(self, elementID, cType):
        if self._elementIsIGRReplaced(elementID, cType):
            return self.__igrReplacedItems[cType][elementID]
        else:
            return None
            return None

    def __onIGRTypeChanged(self, roomType, xpFactor):
        self._update()
