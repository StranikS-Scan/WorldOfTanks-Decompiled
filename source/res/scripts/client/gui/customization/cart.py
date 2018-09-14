# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/cart.py
import functools
import itertools
import BigWorld
from Event import Event
from adisp import async, process
from items import vehicles
from CurrentVehicle import g_currentVehicle
from helpers.i18n import makeString as _ms
from gui import SystemMessages, g_tankActiveCamouflage
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.customization.shared import forEachSlotIn, getAdjustedSlotIndex, elementsDiffer, DURATION, CUSTOMIZATION_TYPE, INSTALLATION
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

    def __init__(self, events, dependencies):
        self._activeCamouflage = dependencies.g_tankActiveCamouflage
        self._currentVehicle = dependencies.g_currentVehicle
        self.__events = events
        self.__displayedElements = None
        self.__elementsToProcess = 1
        self.__purchaseData = []
        self.__initialSlotsData = None
        self.__totalPriceCredits = 0
        self.__totalPriceGold = 0
        self.__isShown = False
        self.__processingMultiplePurchase = False
        self.purchaseProcessed = Event()
        return

    def init(self):
        self.__events.onDisplayedElementsAndGroupsUpdated += self.__saveDisplayedElements
        self.__events.onSlotsSet += self.__update
        self.__events.onInitialSlotsSet += self.__saveInitialSlotsData
        self.__events.onTankSlotCleared += self.__purchaseSingleEventHandler
        self.__events.onOwnedElementPicked += self.__purchaseSingleEventHandler

    def fini(self):
        self.__events.onOwnedElementPicked -= self.__purchaseSingleEventHandler
        self.__events.onTankSlotCleared -= self.__purchaseSingleEventHandler
        self.__events.onInitialSlotsSet -= self.__saveInitialSlotsData
        self.__events.onSlotsSet -= self.__update
        self.__events.onDisplayedElementsAndGroupsUpdated -= self.__saveDisplayedElements
        self.__purchaseData = []
        self.__displayedElements = None
        self.__initialSlotsData = None
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

    @property
    def processingMultiplePurchase(self):
        return self.__processingMultiplePurchase

    def recalculateTotalPrice(self):
        self.__markDuplicates()
        self.__totalPriceCredits = 0
        self.__totalPriceGold = 0
        for item in self.__purchaseData:
            if item['isSelected'] and not item['isDuplicate']:
                price = item['object'].getPrice(item['duration'])
                if item['duration'] == DURATION.PERMANENT:
                    self.__totalPriceGold += price
                else:
                    self.__totalPriceCredits += price

    @process
    def purchaseMultiple(self, purchaseWindowItems):
        self.__processingMultiplePurchase = True
        self.__events.onMultiplePurchaseStarted()
        sortedItems = sorted(zip(purchaseWindowItems, self.__purchaseData), key=lambda (wItem, _): wItem['price'])
        self.__elementsToProcess = len(filter(lambda (wItem, _): wItem['selected'], sortedItems))
        for wItem, cartItem in sortedItems:
            isGold = cartItem['duration'] == DURATION.PERMANENT
            if wItem['selected']:
                yield self.__purchaseSingle(wItem['cType'], cartItem['spot'], getAdjustedSlotIndex(wItem['slotIdx'], wItem['cType'], self.__initialSlotsData), wItem['id'], cartItem['duration'], installationFlag=wItem['price'], isGold=isGold)

    @async
    @process
    def __purchaseSingle(self, cType, cSpot, slotIdx, cItemID, duration, callback, installationFlag=INSTALLATION.REMOVAL, isGold=True):
        purchaseFunction = {CUSTOMIZATION_TYPE.CAMOUFLAGE: BigWorld.player().inventory.changeVehicleCamouflage,
         CUSTOMIZATION_TYPE.EMBLEM: BigWorld.player().inventory.changeVehicleEmblem,
         CUSTOMIZATION_TYPE.INSCRIPTION: BigWorld.player().inventory.changeVehicleInscription}[cType]
        if not (installationFlag > 0 or isGold):
            duration = 0
        arguments = [g_currentVehicle.item.invID,
         cSpot + slotIdx,
         cItemID if installationFlag != INSTALLATION.REMOVAL else 0,
         duration]
        if cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            arguments.append(1)
        if cType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self._activeCamouflage[self._currentVehicle.item.intCD] = slotIdx
        resultID = yield purchaseFunction(*arguments)
        if installationFlag == INSTALLATION.REMOVAL:
            self.__onCustomizationDrop(resultID, cItemID, cType)
        else:
            self.__onCustomizationChange((installationFlag, isGold), cType, resultID)
        callback(resultID)

    @process
    def __purchaseSingleEventHandler(self, *args, **kwargs):
        yield self.__purchaseSingle(*args, **kwargs)

    def __markDuplicates(self):
        duplicateSuspected = []
        toBeDuplicated = []
        for item in self.__purchaseData:
            item['isDuplicate'] = False
            if not item['isSelected']:
                continue
            if item['duration'] == DURATION.PERMANENT and (item['object'].getID(), item['type']) not in toBeDuplicated:
                toBeDuplicated.append((item['object'].getID(), item['type']))
            duplicateSuspected.append(item)

        for item in duplicateSuspected:
            if (item['object'].getID(), item['type']) in toBeDuplicated:
                item['isDuplicate'] = True

    @staticmethod
    def __recalculatePurchaseData(container, newSlotData, oldSlotData, cType, slotIdx):
        newElement = newSlotData['element']
        oldElement = oldSlotData['element']
        if elementsDiffer(oldElement, newElement):
            if newSlotData['isInQuest']:
                return
            container[cType].append({'type': cType,
             'idx': slotIdx,
             'object': newElement,
             'duration': newSlotData['duration'],
             'initialDuration': newSlotData['duration'],
             'spot': newSlotData['spot'],
             'isDuplicate': False,
             'isSelected': True})

    def __synchronizeDossierIfRequired(self):
        self.__elementsToProcess -= 1
        if not self.__elementsToProcess:
            BigWorld.player().resyncDossiers()
            self.__elementsToProcess = 1
            if self.__processingMultiplePurchase:
                self.__events.onMultiplePurchaseProcessed()
                self.__processingMultiplePurchase = False

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
            if cItemID in self.__displayedElements[cType] and self.__displayedElements[cType][cItemID].isInDossier:
                intCD = g_currentVehicle.item.intCD
                vehicle = vehicles.getVehicleType(int(intCD))
                message = _ms(_DROP_MESSAGE[cType]['storedSuccess'], vehicle=vehicle.userString)
            else:
                message = _ms(_DROP_MESSAGE[cType]['removedSuccess'])
            if g_tankActiveCamouflage.has_key(g_currentVehicle.item.intCD):
                del g_tankActiveCamouflage[g_currentVehicle.item.intCD]
        SystemMessages.pushMessage(message, type=sysMessageType)
        self.__synchronizeDossierIfRequired()

    def __saveDisplayedElements(self, displayedElements, displayedGroups):
        self.__displayedElements = displayedElements

    def __saveInitialSlotsData(self, iSlotsData):
        self.__initialSlotsData = iSlotsData

    def __update(self, updatedSlotsData):
        self.__purchaseData = []
        sortedContainer = [[], [], []]
        forEachSlotIn(updatedSlotsData, self.__initialSlotsData, functools.partial(self.__recalculatePurchaseData, sortedContainer))
        self.__purchaseData = list(itertools.chain(*sortedContainer))
        self.recalculateTotalPrice()
        self.__events.onCartUpdated(self.__purchaseData)
        if not self.__totalPriceCredits + self.__totalPriceGold:
            if self.__isShown:
                self.__events.onCartEmptied()
                self.__isShown = False
        elif not self.__isShown:
            self.__events.onCartFilled()
            self.__isShown = True
