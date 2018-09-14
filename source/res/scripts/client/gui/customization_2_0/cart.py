# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization_2_0/cart.py
import functools
import itertools
import BigWorld
from Event import Event
from gui import SystemMessages, g_tankActiveCamouflage
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from data_aggregator import CUSTOMIZATION_TYPE, DURATION
from items import vehicles
from helpers.i18n import makeString as _ms
from shared import forEachSlotIn
from CurrentVehicle import g_currentVehicle
_INSTALLATION_MESSAGE = {CUSTOMIZATION_TYPE.CAMOUFLAGE: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_CHANGE_SERVER_ERROR,
                                 'free': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_FREE,
                                 'successGold': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_GOLD,
                                 'successCredits': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_CHANGE_SUCCESS_CREDITS},
 CUSTOMIZATION_TYPE.EMBLEM: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SERVER_ERROR,
                             'free': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_FREE,
                             'successGold': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_GOLD,
                             'successCredits': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_CREDITS},
 CUSTOMIZATION_TYPE.INSCRIPTION: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SERVER_ERROR,
                                  'free': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_FREE,
                                  'successGold': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_GOLD,
                                  'successCredits': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_CREDITS}}
_DROP_MESSAGE = {CUSTOMIZATION_TYPE.CAMOUFLAGE: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_DROP_SERVER_ERROR,
                                 'storedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_STORED_SUCCESS,
                                 'removedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_CAMOUFLAGE_DROP_SUCCESS},
 CUSTOMIZATION_TYPE.EMBLEM: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_DROP_SERVER_ERROR,
                             'storedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_STORED_SUCCESS,
                             'removedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_DROP_SUCCESS},
 CUSTOMIZATION_TYPE.INSCRIPTION: {'error': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_DROP_SERVER_ERROR,
                                  'storedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_STORED_SUCCESS,
                                  'removedSuccess': SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_DROP_SUCCESS}}

class Cart(object):
    purchaseProcessStarted = Event()

    def __init__(self, aggregatedData):
        self.__elementsToProcess = 1
        self.__aData = aggregatedData
        self.__purchaseData = []
        self.__initialSlotsData = None
        self.__totalPriceCredits = 0
        self.__totalPriceGold = 0
        self.__isShown = False
        self.itemsUpdated = Event()
        self.filled = Event()
        self.emptied = Event()
        self.totalPriceUpdated = Event()
        self.availableMoneyUpdated = Event()
        self.purchaseProcessed = Event()
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__onAvailableMoneyUpdate,
         'stats.gold': self.__onAvailableMoneyUpdate})
        return

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__aData = None
        self.__initialSlotsData = None
        self.__purchaseData = None
        return

    @property
    def items(self):
        return self.__purchaseData

    @property
    def totalPriceGold(self):
        return self.__totalPriceGold

    @property
    def totalPriceCredits(self):
        return self.__totalPriceCredits

    def setInitialSlotsData(self, iSlotsData):
        self.__initialSlotsData = iSlotsData

    def update(self, updatedSlotsData):
        self.__purchaseData = []
        sortedContainer = [[], [], []]
        forEachSlotIn(updatedSlotsData, self.__initialSlotsData, functools.partial(self.__recalculatePurchaseData, sortedContainer))
        self.__purchaseData = list(itertools.chain(*sortedContainer))
        self.markDuplicates()
        self.recalculateTotalPrice()
        self.itemsUpdated(self.__purchaseData)
        self.totalPriceUpdated()
        if not bool(self.__totalPriceCredits + self.__totalPriceGold):
            if self.__isShown:
                self.emptied()
                self.__isShown = False
        elif not self.__isShown:
            self.filled()
            self.__isShown = True

    def buyItems(self, purchaseWindowItems):
        sortedItems = sorted(purchaseWindowItems, key=lambda item: item['price'])
        self.__elementsToProcess = 0
        for item in sortedItems:
            if item['selected']:
                self.__elementsToProcess += 1

        self.purchaseProcessStarted()
        for item in sortedItems:
            itemIndex = purchaseWindowItems.index(item)
            cartItem = self.__purchaseData[itemIndex]
            isGold = cartItem['duration'] == DURATION.PERMANENT
            if item['selected']:
                self.buyItem(item['cType'], cartItem['spot'], self.__calculateVehicleIndex(item['slotIdx'], item['cType']), item['id'], cartItem['duration'], item['price'], isGold)

    def buyItem(self, cType, cSpot, slotIdx, cItemID, duration, price=-1, isGold=True):
        purchaseFunction = {CUSTOMIZATION_TYPE.CAMOUFLAGE: BigWorld.player().inventory.changeVehicleCamouflage,
         CUSTOMIZATION_TYPE.EMBLEM: BigWorld.player().inventory.changeVehicleEmblem,
         CUSTOMIZATION_TYPE.INSCRIPTION: BigWorld.player().inventory.changeVehicleInscription}[cType]
        if not (price > 0 or isGold):
            duration = 0
        arguments = [g_currentVehicle.item.invID,
         cSpot + slotIdx,
         cItemID if price != -1 else 0,
         duration]
        if cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            arguments.append(1)
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = slotIdx
        if price == -1:
            arguments.append(lambda resultID: self.__onCustomizationDrop(resultID, cItemID, cType))
        else:
            arguments.append(functools.partial(self.__onCustomizationChange, (price, isGold), cType))
        purchaseFunction(*arguments)

    def markDuplicates(self):
        duplicateSuspected = []
        toBeDuplicated = []
        for item in self.__purchaseData:
            item['isDuplicate'] = False
            if not item['isSelected']:
                continue
            if item['duration'] == DURATION.PERMANENT and (item['itemID'], item['type']) not in toBeDuplicated:
                toBeDuplicated.append((item['itemID'], item['type']))
            duplicateSuspected.append(item)

        for item in duplicateSuspected:
            if (item['itemID'], item['type']) in toBeDuplicated:
                item['isDuplicate'] = True

    def recalculateTotalPrice(self):
        self.__totalPriceCredits = 0
        self.__totalPriceGold = 0
        for item in self.__purchaseData:
            if item['isSelected'] and not item['isDuplicate']:
                price = item['object'].getPrice(item['duration'])
                if item['duration'] == DURATION.PERMANENT:
                    self.__totalPriceGold += price
                else:
                    self.__totalPriceCredits += price

    def __recalculatePurchaseData(self, container, newSlotItem, oldSlotItem, cType, slotIdx):
        if newSlotItem['itemID'] != oldSlotItem['itemID'] and newSlotItem['itemID'] > 0:
            cItem = self.__aData.available[cType][newSlotItem['itemID']]
            if newSlotItem['purchaseTypeIcon'] == RES_ICONS.MAPS_ICONS_LIBRARY_QUEST_ICON:
                return
            container[cType].append({'type': cType,
             'idx': slotIdx,
             'object': cItem,
             'itemID': newSlotItem['itemID'],
             'bonus': newSlotItem['bonus'],
             'name': cItem.getName(),
             'bonusValue': cItem.qualifier.getValue(),
             'bonusIcon': cItem.qualifier.getIcon16x16(),
             'duration': newSlotItem['duration'],
             'initialDuration': newSlotItem['duration'],
             'spot': newSlotItem['spot'],
             'isConditional': '' if cItem.qualifier.getDescription() is None else '*',
             'isDuplicate': False,
             'isSelected': True})
        return

    def __synchronizeDossierIfRequired(self):
        self.__elementsToProcess -= 1
        if self.__elementsToProcess == 0:
            BigWorld.player().resyncDossiers()
            self.__elementsToProcess = 1
            self.purchaseProcessed()

    def __onAvailableMoneyUpdate(self, *args):
        self.availableMoneyUpdated()

    def __onCustomizationChange(self, price, cType, resultID):
        if resultID < 0:
            message = _ms(_INSTALLATION_MESSAGE[cType]['error'])
            sysMessageType = SystemMessages.SM_TYPE.Error
        else:
            cost, isGold = price
            if cost <= 0:
                message = _ms(_INSTALLATION_MESSAGE[cType]['free'])
                sysMessageType = SystemMessages.SM_TYPE.Information
            else:
                if isGold:
                    key = _INSTALLATION_MESSAGE[cType]['successGold']
                    fCost = BigWorld.wg_getGoldFormat(cost)
                    sysMessageType = SystemMessages.SM_TYPE.CustomizationForGold
                else:
                    key = _INSTALLATION_MESSAGE[cType]['successCredits']
                    fCost = BigWorld.wg_getIntegralFormat(cost)
                    sysMessageType = SystemMessages.SM_TYPE.CustomizationForCredits
                message = _ms(key, fCost)
        SystemMessages.pushMessage(message, type=sysMessageType)
        self.__synchronizeDossierIfRequired()

    def __onCustomizationDrop(self, resultID, cItemID, cType):
        if resultID < 0:
            message = _ms(_DROP_MESSAGE[cType]['error'])
            sysMessageType = SystemMessages.SM_TYPE.Error
        else:
            sysMessageType = SystemMessages.SM_TYPE.Information
            if self.__aData.available[cType][cItemID].isInDossier:
                intCD = g_currentVehicle.item.intCD
                vehicle = vehicles.getVehicleType(int(intCD))
                message = _ms(_DROP_MESSAGE[cType]['storedSuccess'], vehicle=vehicle.userString)
            else:
                message = _ms(_DROP_MESSAGE[cType]['removedSuccess'])
            if g_tankActiveCamouflage.has_key(g_currentVehicle.item.intCD):
                del g_tankActiveCamouflage[g_currentVehicle.item.intCD]
        SystemMessages.pushMessage(message, type=sysMessageType)
        self.__synchronizeDossierIfRequired()

    def __calculateVehicleIndex(self, initialIndex, cType):
        if initialIndex == 1:
            slotItem = self.__initialSlotsData['data'][cType]['data'][initialIndex]
            adjacentSlotItem = self.__initialSlotsData['data'][cType]['data'][0]
            if slotItem['spot'] != adjacentSlotItem['spot']:
                return initialIndex - 1
            else:
                return initialIndex
        return initialIndex
