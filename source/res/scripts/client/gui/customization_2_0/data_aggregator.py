# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization_2_0/data_aggregator.py
import copy
from collections import namedtuple
from Event import Event
import nations
from gui import GUI_SETTINGS, g_tankActiveCamouflage
from gui.game_control import getIGRCtrl, g_instance as _g_gameControlInstance
from gui.server_events import g_eventsCache as _g_eventsCache
from gui.shared import g_itemsCache as _g_itemsCache
from gui.shared.ItemsCache import CACHE_SYNC_REASON, g_itemsCache
from items.vehicles import g_cache as _g_vehiclesCache
from items.qualifiers import g_cache as _g_qualifiersCache
from CurrentVehicle import g_currentVehicle as _g_currentVehicle, g_currentVehicle
from elements import AvailableCamouflage, AvailableInscription, AvailableEmblem, InstalledCamouflage, InstalledInscription, InstalledEmblem, Qualifier, CamouflageQualifier
_QuestData = namedtuple('QuestData', ('id', 'isCompleted', 'name', 'count'))

class CUSTOMIZATION_TYPE(object):
    CAMOUFLAGE = 0
    EMBLEM = 1
    INSCRIPTION = 2
    ALL = (CAMOUFLAGE, EMBLEM, INSCRIPTION)


class DURATION(object):
    PERMANENT = 0
    MONTH = 30
    WEEK = 7
    ALL = (PERMANENT, MONTH, WEEK)


SLOT_TYPE = {CUSTOMIZATION_TYPE.EMBLEM: 'player',
 CUSTOMIZATION_TYPE.INSCRIPTION: 'inscription'}
TYPE_NAME = {'emblems': CUSTOMIZATION_TYPE.EMBLEM,
 'inscriptions': CUSTOMIZATION_TYPE.INSCRIPTION,
 'camouflages': CUSTOMIZATION_TYPE.CAMOUFLAGE}
_ITEM_CLASS = {CUSTOMIZATION_TYPE.EMBLEM: AvailableEmblem,
 CUSTOMIZATION_TYPE.INSCRIPTION: AvailableInscription,
 CUSTOMIZATION_TYPE.CAMOUFLAGE: AvailableCamouflage}
_ITEM_CONTAINER = {CUSTOMIZATION_TYPE.CAMOUFLAGE: lambda nationId, itemId: _g_vehiclesCache.customization(nationId)['camouflages'][itemId],
 CUSTOMIZATION_TYPE.EMBLEM: lambda _, itemId: _g_vehiclesCache.playerEmblems()[1][itemId],
 CUSTOMIZATION_TYPE.INSCRIPTION: lambda nationId, itemId: _g_vehiclesCache.customization(nationId)['inscriptions'][itemId]}
_ITEM_GROUP = {CUSTOMIZATION_TYPE.CAMOUFLAGE: lambda nationId: _g_vehiclesCache.customization(nationId)['camouflageGroups'],
 CUSTOMIZATION_TYPE.EMBLEM: lambda _: _g_vehiclesCache.playerEmblems()[0],
 CUSTOMIZATION_TYPE.INSCRIPTION: lambda nationId: _g_vehiclesCache.customization(nationId)['inscriptionGroups']}
_MAX_HULL_SLOTS = 2
_MAX_TURRET_SLOTS = 2
VEHICLE_CHANGED_EVENT = 'VEHICLE_CHANGED_EVENT'
EVENTS_UPDATED_EVENT = 'EVENTS_UPDATED_EVENT'
_IGR_TYPE_CHANGED = 'IGR_TYPE_CHANGED'

class DataAggregator(object):

    def __init__(self):
        self.updated = Event()
        self.viewModel = []
        self.__installed = ()
        self.__availableItems = None
        self.__displayedItems = None
        self.__associatedQuests = None
        self.__igrReplacedItems = None
        self.__notMigratedItems = None
        self.__itemGroups = None
        self.__initialViewModel = ()
        self.__cNationID = None
        self.__rawItems = None
        self.__vehicleInventoryID = None
        self.__displayIgrItems = False
        self.__availableGroupNames = None
        return

    def init(self):
        self.__gatherDataForVehicle(CACHE_SYNC_REASON.DOSSIER_RESYNC, None)
        _g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        _g_itemsCache.onSyncCompleted += self.__gatherDataForVehicle
        _g_eventsCache.onSyncCompleted += self.__onEventsUpdated
        _g_gameControlInstance.igr.onIgrTypeChanged += self.__onIGRTypeChanged
        return

    def fini(self):
        _g_gameControlInstance.igr.onIgrTypeChanged -= self.__onIGRTypeChanged
        _g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        _g_itemsCache.onSyncCompleted -= self.__gatherDataForVehicle
        _g_eventsCache.onSyncCompleted -= self.__onEventsUpdated
        self.__rawItems = None
        self.__installed = None
        self.__availableItems = None
        self.__notMigratedItems = None
        self.__displayedItems = None
        self.__initialViewModel = None
        self.__availableGroupNames = None
        self.__igrReplacedItems = None
        self.__itemGroups = None
        self.viewModel = None
        return

    @property
    def installed(self):
        return self.__installed

    @property
    def available(self):
        return self.__availableItems

    @property
    def displayed(self):
        return self.__displayedItems

    @property
    def associatedQuests(self):
        return self.__associatedQuests

    @property
    def initialViewModel(self):
        return self.__initialViewModel

    @property
    def availableGroupNames(self):
        return self.__availableGroupNames

    def __onCurrentVehicleChanged(self):
        if self.__vehicleInventoryID != g_currentVehicle.item.invID:
            self.__gatherDataForVehicle(VEHICLE_CHANGED_EVENT, None)
        return

    def __onEventsUpdated(self):
        self.__gatherDataForVehicle(EVENTS_UPDATED_EVENT, None)
        return

    def __onIGRTypeChanged(self, roomType, xpFactor):
        self.__gatherDataForVehicle(_IGR_TYPE_CHANGED, None)
        return

    def __gatherDataForVehicle(self, updateReason, invalidItems):
        if updateReason in (CACHE_SYNC_REASON.DOSSIER_RESYNC,
         CACHE_SYNC_REASON.SHOP_RESYNC,
         _IGR_TYPE_CHANGED,
         VEHICLE_CHANGED_EVENT,
         EVENTS_UPDATED_EVENT):
            self.__displayIgrItems = getIGRCtrl().getRoomType() == 2 and GUI_SETTINGS.igrEnabled
            self.__vehicleInventoryID = g_currentVehicle.item.invID
            curVehItem = _g_currentVehicle.item
            curVehDescr = curVehItem.descriptor
            self.__cNationID = curVehDescr.type.customizationNationID
            inDossier = (_g_itemsCache.items.getVehicleDossier(curVehItem.intCD).getBlock('camouflages'), _g_itemsCache.items.getVehicleDossier(curVehItem.intCD).getBlock('emblems'), _g_itemsCache.items.getVehicleDossier(curVehItem.intCD).getBlock('inscriptions'))
            self.__rawItems = [_g_vehiclesCache.customization(self.__cNationID)['camouflages'], _g_vehiclesCache.playerEmblems()[1], _g_vehiclesCache.customization(self.__cNationID)['inscriptions']]
            self.__itemGroups = (_g_vehiclesCache.customization(self.__cNationID)['camouflageGroups'], _g_vehiclesCache.playerEmblems()[0], _g_vehiclesCache.customization(self.__cNationID)['inscriptionGroups'])
            inQuests = self.__getQuestItems()
            self.__availableGroupNames = [set([]), set([]), set([])]
            self.__displayedItems = [{}, {}, {}]
            self.__availableItems = [{}, {}, {}]
            self.__igrReplacedItems = [{}, {}, {}]
            self.__notMigratedItems = [set([]), set([]), set([])]
            self.__associatedQuests = [{}, {}, {}]
            inventoryItems = self.getInventoryItems(self.__cNationID, self.__rawItems)
            installedRawItems = self.__setInstalledRawItems(curVehDescr)
            self.__installed = self.__setInstalledCustomization(curVehDescr.hull['emblemSlots'], curVehDescr.turret['emblemSlots'], installedRawItems)
            for cType in CUSTOMIZATION_TYPE.ALL:
                self.__fillAvailableItems(cType, inDossier, inQuests, inventoryItems)
                self.__fillDisplayedItems(cType)
                self.__fillDisplayedGroups(cType)

            if updateReason == VEHICLE_CHANGED_EVENT:
                needReset = True
            elif updateReason == EVENTS_UPDATED_EVENT:
                needReset = self.__isQuestsChanged(inQuests)
            else:
                needReset = False
            self.__associatedQuests = inQuests
            self.updated(needReset)

    def __setInstalledCustomization(self, vehicleHullSlots, vehicleTurretSlots, installedRawItems):
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
                installedTurretInscriptions.append(installedRawItems['inscriptions'][_MAX_HULL_SLOTS + turretInscriptionSlotIdx])
                turretInscriptionSlotIdx += 1

        return ([ InstalledCamouflage(ic, 0) for ic in installedRawItems['camouflages'] ], [ InstalledEmblem(ihe, 0) for ihe in installedHullEmblems ] + [ InstalledEmblem(ite, 2) for ite in installedTurretEmblems ], [ InstalledInscription(ihi, 0) for ihi in installedHullInscriptions ] + [ InstalledInscription(iti, 2) for iti in installedTurretInscriptions ])

    def __setInstalledRawItems(self, curVehDescr):
        installedRawItems = {'camouflages': list(curVehDescr.camouflages),
         'emblems': list(curVehDescr.playerEmblems),
         'inscriptions': list(curVehDescr.playerInscriptions)}
        for key in installedRawItems.keys():
            for installedRawItem in installedRawItems[key]:
                installedItemID = installedRawItem[0]
                if installedRawItem[2] == 0 and installedItemID is not None and (TYPE_NAME[key] != CUSTOMIZATION_TYPE.EMBLEM or TYPE_NAME[key] == CUSTOMIZATION_TYPE.EMBLEM) and installedItemID not in self.__itemGroups[CUSTOMIZATION_TYPE.EMBLEM]['auto'][0]:
                    self.__notMigratedItems[TYPE_NAME[key]].add(installedItemID)

        if self.__displayIgrItems:
            vehicleId = g_currentVehicle.item.invID
            igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
            igrRoomType = getIGRCtrl().getRoomType()
            igrVehDescr = []
            if vehicleId in igrLayout:
                if igrRoomType in igrLayout[vehicleId]:
                    igrVehDescr = igrLayout[vehicleId][igrRoomType]
            for key in igrVehDescr:
                for index in igrVehDescr[key]:
                    replacedItemID = installedRawItems[key][index][0]
                    replacedItemDaysLeft = installedRawItems[key][index][2]
                    if replacedItemID is not None:
                        self.__igrReplacedItems[TYPE_NAME[key]][replacedItemID] = replacedItemDaysLeft
                    installedRawItems[key][index] = igrVehDescr[key][index]

        activeCamouflage = g_tankActiveCamouflage['historical'].get(curVehDescr.type.compactDescr)
        if activeCamouflage is None:
            activeCamouflage = g_tankActiveCamouflage.get(curVehDescr.type.compactDescr, 0)
        camouflageID = curVehDescr.camouflages[activeCamouflage][0]
        self.__initialViewModel = (camouflageID, installedRawItems['emblems'], installedRawItems['inscriptions'])
        self.viewModel = [camouflageID, copy.deepcopy(installedRawItems['emblems']), copy.deepcopy(installedRawItems['inscriptions'])]
        return installedRawItems

    def __fillAvailableItems(self, cType, inDossier, inQuests, inventoryItems):
        containerToFill = self.__availableItems[cType]
        availableRawItems = self.__rawItems[cType]
        for itemID, availableRawItem in availableRawItems.iteritems():
            replacedByIGRItem = itemID in self.__igrReplacedItems[cType]
            isMigrated = itemID not in self.__notMigratedItems[cType]
            isInDossier = itemID in inDossier[cType] or replacedByIGRItem or not isMigrated
            containerToFill[itemID] = self.createElement(itemID, cType, self.__cNationID, isInDossier, itemID in inQuests[cType], replacedByIGRItem, inventoryItems=inventoryItems)

    def createElement(self, itemId, itemType, nationId, isInDossier=False, isInQuests=False, isReplacedByIGR=False, inventoryItems=None):
        rawItemGetter = _ITEM_CONTAINER[itemType]
        groupsGetter = _ITEM_GROUP[itemType]
        rawItem = rawItemGetter(nationId, itemId)
        groups = groupsGetter(nationId)
        cls = _ITEM_CLASS[itemType]
        if itemType != CUSTOMIZATION_TYPE.CAMOUFLAGE:
            if rawItem[7] in _g_qualifiersCache.qualifiers:
                qualifier = Qualifier(_g_qualifiersCache.qualifiers[rawItem[7]])
            else:
                qualifier = CamouflageQualifier('winter')
            group = groups[rawItem[0]]
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
            groupName = rawItem['groupName']
            qualifier = CamouflageQualifier(groupName[3:] if groupName.startswith('IGR') else groupName)
            allowedNations = None
            allowedVehicles = list(rawItem['allow'])
            notAllowedVehicles = rawItem['deny']
            readableGroupName = '#vehicle_customization:camouflage/{0}'.format(groupName[3:] if groupName.startswith('IGR') else groupName)
        numberOfDays = None
        numberOfItems = None
        if itemType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            groupName = itemId
        else:
            groupName = rawItem[0]
        isInShop = self.__groupIsInShop(groupName, itemType, nationId)
        if inventoryItems is not None:
            if itemId in inventoryItems[itemType] and not isInDossier:
                isInDossier = True
                allowedVehicles += inventoryItems[itemType][itemId][4]
                if inventoryItems[itemType][itemId][6][0]:
                    numberOfItems = inventoryItems[itemType][itemId][6][1]
                else:
                    numberOfDays = inventoryItems[itemType][itemId][6][1]
            elif itemId in self.__igrReplacedItems[itemType]:
                numberOfDays = self.__igrReplacedItems[itemType][itemId]
        notAllowedNations = None if allowedNations is None else []
        if allowedNations is not None:
            for nationID in nations.INDICES.values():
                if nationID not in allowedNations:
                    notAllowedNations.append(nationID)

        if itemType == CUSTOMIZATION_TYPE.EMBLEM:
            actualNationId = nations.NONE_INDEX
        else:
            actualNationId = nationId
        return cls(itemId, actualNationId, rawItem, qualifier, isInDossier, isInQuests, isInShop, allowedVehicles, notAllowedVehicles, allowedNations, notAllowedNations, isReplacedByIGR, numberOfItems, numberOfDays, readableGroupName)

    def getInventoryItems(self, cNationID, rawItems=None):
        inventoryItems = ({}, {}, {})
        inventoryCustomization = g_itemsCache.items.inventory.getItemsData('customizations')
        for isGold, itemsData in inventoryCustomization.iteritems():
            if itemsData:
                for key in (None, g_currentVehicle.item.intCD):
                    if key not in itemsData:
                        continue
                    typedItemsData = itemsData[key]
                    for cTypeName, items in typedItemsData.iteritems():
                        cType = TYPE_NAME[cTypeName]
                        for item, itemNum in items.iteritems():
                            if cType != CUSTOMIZATION_TYPE.EMBLEM:
                                nationID, itemID = item
                            else:
                                nationID, itemID = None, item
                            allowedVehicles = []
                            if key is not None:
                                allowedVehicles.append(key)
                            if cNationID == nationID or cType == CUSTOMIZATION_TYPE.EMBLEM:
                                inventoryItems[cType][itemID] = [itemID,
                                 None if rawItems is None else rawItems[cType][itemID],
                                 None,
                                 isGold,
                                 allowedVehicles,
                                 [],
                                 (isGold, itemNum)]

        return inventoryItems

    def __fillDisplayedItems(self, cType):
        containerToFill = self.__displayedItems[cType]
        for itemID, availableItem in self.__availableItems[cType].iteritems():
            if availableItem.isAllowedForCurrentVehicle:
                if availableItem.isInDossier:
                    containerToFill[itemID] = availableItem
                elif availableItem.isInQuests:
                    containerToFill[itemID] = availableItem
                elif availableItem.isInShop:
                    containerToFill[itemID] = availableItem

    def __groupIsInShop(self, groupName, cType, nationID):
        return [lambda group: group not in g_itemsCache.items.shop.getCamouflagesHiddens(nationID), lambda group: group not in g_itemsCache.items.shop.getEmblemsGroupHiddens() and (group != 'group5' or self.__displayIgrItems), lambda group: group not in g_itemsCache.items.shop.getInscriptionsGroupHiddens(nationID) and (group != 'IGR' or self.__displayIgrItems)][cType](groupName)

    def __fillDisplayedGroups(self, cType):
        groups = self.__availableGroupNames[cType]
        for itemID, item in self.__displayedItems[cType].iteritems():
            groupName = item.getGroup()
            if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
                userFriendlyNameKey = 'userString'
            else:
                userFriendlyNameKey = 1
            groups.add((groupName, self.__itemGroups[cType][groupName][userFriendlyNameKey]))

    def __getQuestItems(self):
        questItems = ({}, {}, {})
        for name, event in _g_eventsCache.getEvents().items():
            for bonus in event.getBonuses('customizations'):
                for item in bonus.getList():
                    if item['nationId'] == self.__cNationID or item['type'] == CUSTOMIZATION_TYPE.EMBLEM:
                        questData = _QuestData(id=event.getID(), isCompleted=event.isCompleted(), name=event.getUserName(), count=item['value'])
                        questItems[item['type']][item['id']] = questData

        return questItems

    def __isQuestsChanged(self, newQuests):
        for cType in CUSTOMIZATION_TYPE.ALL:
            if set(newQuests[cType].keys()) != set(self.__associatedQuests[cType].keys()):
                return True
            for itemID, newQuest in newQuests[cType].items():
                oldQuest = self.__associatedQuests[cType][itemID]
                if newQuest.isCompleted and not oldQuest.isCompleted:
                    return True

        return False
