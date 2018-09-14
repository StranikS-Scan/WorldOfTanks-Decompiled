# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/VehicleCustomization.py
import BigWorld
from collections import defaultdict
from functools import partial
from gui.server_events import g_eventsCache
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from adisp import process
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, DialogsInterface, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.customization.VehicleCustonizationModel import VehicleCustomizationModel
from gui.Scaleform.daapi.view.lobby.customization import _VEHICLE_CUSTOMIZATIONS
from gui.Scaleform.daapi.view.lobby.customization import CustomizationHelper
from gui.Scaleform.daapi.view.meta.VehicleCustomizationMeta import VehicleCustomizationMeta
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, I18nInfoDialogMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared import g_itemsCache
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.events import LobbySimpleEvent
from gui.shared.utils.HangarSpace import g_hangarSpace
from helpers import i18n
from shared_utils import findFirst
from items import vehicles
from items.vehicles import VehicleDescr
from account_helpers.settings_core.settings_constants import TUTORIAL

class VehicleCustomization(VehicleCustomizationMeta, View):

    def __init__(self, ctx = None):
        super(VehicleCustomization, self).__init__()
        self.__interfaces = {}
        self.__prevCameraLocation = None
        self.__steps = 0
        self.__messages = []
        self.__credits = 0
        self.__gold = 0
        self.__returnHangar = False
        self.__lockUpdate = False
        self.__onceDataInited = False
        self.__currentSection = None
        self.__isIgrChanged = False
        return

    def getInterface(self, section):
        return self.__interfaces.get(section)

    def _populate(self):
        BigWorld.player().resyncDossiers()
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIDE_HANGAR, True))
        View._populate(self)
        credits, gold = g_itemsCache.items.stats.money
        self.as_setCreditsS(credits)
        self.as_setGoldS(gold)
        g_playerEvents.onDossiersResync += self.__pe_onDossiersResync
        g_clientUpdateManager.addCallbacks({'stats.gold': self.onGoldUpdate,
         'stats.credits': self.onCreditsUpdate,
         'cache.mayConsumeWalletResources': self.onGoldUpdate,
         'account.attrs': self.onCameraUpdate,
         'inventory.1.compDescr': self.onVehiclesUpdate,
         'cache.vehsLock': self.__cv_onChanged})
        g_itemsCache.onSyncCompleted += self.__pe_onShopResync
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIGRTypeChanged
        g_currentVehicle.onChanged += self.__cv_onChanged
        g_hangarSpace.onSpaceCreate += self.__hs_onSpaceCreate
        g_eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        vehDescr = None
        vehType = None
        if g_currentVehicle.isPresent():
            vehDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
            vehType = vehDescr.type
            VehicleCustomizationModel.setVehicleDescriptor(vehDescr)
        self.__steps = len(_VEHICLE_CUSTOMIZATIONS)
        for customization in _VEHICLE_CUSTOMIZATIONS:
            sectionName = customization['sectionName']
            interface = customization['interface'](sectionName, vehDescr.type.customizationNationID, customization['type'], customization['position'])
            interface.onDataInited += self.__ci_onDataInited
            interface.onCustomizationChangeSuccess += self.__ci_onCustomizationChangeSuccess
            interface.onCustomizationChangeFailed += self.__ci_onCustomizationChangeFailed
            interface.onCustomizationDropSuccess += self.__ci_onCustomizationDropSuccess
            interface.onCustomizationDropFailed += self.__ci_onCustomizationDropFailed
            interface.onCurrentItemChange += self.__ci_onCurrentItemChanged
            self.__interfaces[sectionName] = interface
            interface.updateSlotsPosition(vehDescr)
            interface.setFlashObject(self.flashObject, setScript=False)
            interface.fetchCurrentItem(vehDescr)
            interface.invalidateViewData(vehType)

        if not self.__steps:
            self.__finishInitData()
        self.setupContextHints(TUTORIAL.CUSTOMIZATION)
        return

    def _dispose(self):
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIDE_HANGAR, False))
        self.__resetPreviewMode()
        for interface in self.__interfaces.itervalues():
            interface.destroy()
            interface.onDataInited -= self.__ci_onDataInited
            interface.onCustomizationChangeSuccess -= self.__ci_onCustomizationChangeSuccess
            interface.onCustomizationChangeFailed -= self.__ci_onCustomizationChangeFailed
            interface.onCustomizationDropSuccess -= self.__ci_onCustomizationDropSuccess
            interface.onCustomizationDropFailed -= self.__ci_onCustomizationDropFailed
            interface.onCurrentItemChange -= self.__ci_onCurrentItemChanged

        self.__interfaces.clear()
        self.__onceDataInited = False
        g_itemsCache.onSyncCompleted -= self.__pe_onShopResync
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onIGRTypeChanged
        g_currentVehicle.onChanged -= self.__cv_onChanged
        g_hangarSpace.onSpaceCreate -= self.__hs_onSpaceCreate
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        g_playerEvents.onDossiersResync -= self.__pe_onDossiersResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        CustomizationHelper.clearStoredCustomizationData()
        View._dispose(self)

    def __onServerResponsesReceived(self):
        self.as_onServerResponsesReceivedS()
        self.__lockUpdate = False
        Waiting.hide('customizationApply')
        for type, message in self.__messages:
            SystemMessages.pushMessage(message, type=type)

        self.__messages = []
        BigWorld.player().resyncDossiers()
        if self.__returnHangar:
            self.closeWindow()
        else:
            self.__refreshData()

    def __refreshData(self):
        vehType = vehicles.g_cache.vehicle(*g_currentVehicle.item.descriptor.type.id)
        updatedDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
        for interface in self.__interfaces.itervalues():
            interface.update(updatedDescr)
            interface.fetchCurrentItem(updatedDescr)
            interface.refreshViewData(vehType, refresh=True)

        self.as_refreshDataS()

    def __finishInitData(self):
        if not self.__onceDataInited:
            self.__requestMoney()
            self.as_onInitS(self._getSections())
            if g_currentVehicle.isLocked() or g_currentVehicle.isBroken():
                self.as_setActionsLockedS(True)
            self.__setPreviewMode()
            self.__onceDataInited = True

    def __requestMoney(self):
        self.__credits, self.__gold = g_itemsCache.items.stats.money

    def _getSections(self):
        res = []
        for customization in _VEHICLE_CUSTOMIZATIONS:
            res.append({'sectionName': customization['sectionName'],
             'sectionLabel': customization['sectionUserString'],
             'priceLabel': customization['priceUserString'],
             'linkage': customization['linkage'],
             'enabled': self.getInterface(customization['sectionName']).isEnabled(),
             'type': customization['type'],
             'showNewMarker': self.getInterface(customization['sectionName']).hasNewItems()})

        return res

    def __setPreviewMode(self):
        space = g_hangarSpace.space
        if space is not None:
            self.__prevCameraLocation = space.getCameraLocation()
            space.locateCameraToPreview()
        else:
            LOG_ERROR("ClientHangarSpace isn't initialized")
        return

    def __resetPreviewMode(self):
        space = g_hangarSpace.space
        if space is not None and self.__prevCameraLocation is not None:
            space.setCameraLocation(**self.__prevCameraLocation)
            space.clearSelectedEmblemInfo()
        return

    def closeWindow(self):
        self.destroy()

    def __ci_onDataInited(self, _):
        self.__steps -= 1
        if not self.__steps:
            self.__finishInitData()

    def __ci_onCustomizationChangeFailed(self, message):
        self.__returnHangar = False
        self.__messages.append((SystemMessages.SM_TYPE.Error, message))
        self.__steps -= 1
        if not self.__steps:
            self.__onServerResponsesReceived()

    def __ci_onCustomizationChangeSuccess(self, message, type):
        self.as_onChangeSuccessS()
        self.__messages.append((type, message))
        self.__steps -= 1
        if not self.__steps:
            self.__onServerResponsesReceived()

    def __ci_onCustomizationDropFailed(self, message):
        Waiting.hide('customizationDrop')
        self.__lockUpdate = False
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)

    def __ci_onCurrentItemChanged(self, section):
        self.as_onCurrentChangedS(section)

    def __ci_onCustomizationDropSuccess(self, message):
        self.as_onDropSuccessS()
        Waiting.hide('customizationDrop')
        self.__lockUpdate = False
        BigWorld.player().resyncDossiers()
        self.__refreshData()
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Information)

    def __hs_onSpaceCreate(self):
        space = g_hangarSpace.space
        if space:
            self.__prevCameraLocation = space.getCameraLocation()
            if self.__currentSection:
                self.getCurrentItem(self.__currentSection)
            else:
                space.locateCameraToPreview()

    def __onEventsCacheSyncCompleted(self):
        self.__refreshData()

    def onGoldUpdate(self, value):
        value = g_itemsCache.items.stats.gold
        self.__gold = value
        self.as_setGoldS(value)

    def onCreditsUpdate(self, value):
        value = g_itemsCache.items.stats.credits
        self.__credits = value
        self.as_setCreditsS(value)

    def onCameraUpdate(self, *args):
        self.__prevCameraLocation.update({'yaw': None,
         'pitch': None})
        return

    def onVehiclesUpdate(self, vehicles):
        if vehicles is None or self.__lockUpdate:
            return
        else:
            vehCompDescr = vehicles.get(g_currentVehicle.invID)
            if vehCompDescr is not None:
                vehDescr = VehicleDescr(compactDescr=vehCompDescr)
                for interface in self.__interfaces.itervalues():
                    interface.update(CustomizationHelper.getUpdatedDescriptor(vehDescr))

                self.as_refreshItemsDataS()
            return

    def __pe_onDossiersResync(self):
        self.as_refreshItemsDataS()

    def __pe_onShopResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.SHOP_RESYNC or not g_currentVehicle.isPresent():
            return
        self.__steps = len(_VEHICLE_CUSTOMIZATIONS)
        vehType = vehicles.g_cache.vehicle(*g_currentVehicle.item.descriptor.type.id)
        for interface in self.__interfaces.itervalues():
            interface.invalidateViewData(vehType, refresh=True)

    def __onIGRTypeChanged(self, roomType, xpFactor):
        LOG_DEBUG('__onIGRTypeChanged', roomType, xpFactor)
        if not g_currentVehicle.isPresent():
            return
        self.__steps = len(_VEHICLE_CUSTOMIZATIONS)
        vehType = vehicles.g_cache.vehicle(*g_currentVehicle.item.descriptor.type.id)
        vehDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
        VehicleCustomizationModel.resetVehicleDescriptor(vehDescr)
        for interface in self.__interfaces.itervalues():
            interface.update(CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor))
            interface.refreshViewData(vehType, refresh=True)

        self.as_refreshDataS()
        self.as_onResetNewItemS()
        self.__isIgrChanged = True

    def __cv_onChanged(self, *args):
        if self.__steps:
            return
        if not g_currentVehicle.isReadyToFight() and not g_currentVehicle.isReadyToPrebattle():
            if g_currentVehicle.isCrewFull() and not g_currentVehicle.isBroken():
                self.closeWindow()
        else:
            self.as_setActionsLockedS(g_currentVehicle.isLocked() or g_currentVehicle.isBroken() or g_currentVehicle.isDisabledInRent())

    def setNewItemId(self, section, itemId, kind, packageIdx):
        interface = self.__interfaces.get(section)
        if interface is not None:
            interface.onSetID(int(itemId), int(kind), int(packageIdx))
        return

    def getCurrentItem(self, section):
        g_hangarSpace.space.clearSelectedEmblemInfo()
        self.__currentSection = section
        interface = self.__interfaces.get(section)
        if interface is not None:
            return interface.getCurrentItem()
        else:
            return
            return

    def getItemCost(self, section, itemId, priceIndex):
        interface = self.__interfaces.get(section)
        if interface is not None:
            return interface.getItemCost(itemId, priceIndex)
        else:
            return
            return

    @process
    def applyCustomization(self, sections):
        if g_currentVehicle.isLocked():
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_VEHICLE_LOCKED, type=SystemMessages.SM_TYPE.Error)
            yield lambda callback = None: callback
        if g_currentVehicle.isBroken():
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.customization_vehicle(g_currentVehicle.item.getState()), type=SystemMessages.SM_TYPE.Error)
            yield lambda callback = None: callback
        notSelected = []
        selected = []
        remove = []
        selectedNames = []
        totalGold = 0
        totalCredits = 0
        newItemsByType = defaultdict(list)
        for section in sections:
            interface = self.__interfaces.get(section.sectionName)
            if interface is not None:
                newItems = interface.getNewItems()
                if newItems is not None:
                    self.__updateNewItemsByType(newItemsByType, newItems, interface._type)

        for section in sections:
            interface = self.__interfaces.get(section.sectionName)
            if interface is not None:
                newItems = interface.getNewItems()
                if newItems is not None:
                    removeStr = None
                    hasMatches = self.__hasNewItemsDuplicates(newItemsByType, newItems, interface._type)
                    if not hasMatches:
                        costValue = interface.getSelectedItemCost()
                        if type(costValue) is list:
                            for price in costValue:
                                cost = price.get('cost')
                                isGold = price.get('isGold')
                                if cost > 0:
                                    if isGold and section.isGold:
                                        totalGold += cost
                                    elif not isGold and not section.isGold:
                                        totalCredits += cost

                        else:
                            cost, isGold = costValue
                            if cost > 0:
                                if isGold:
                                    totalGold += cost
                                else:
                                    totalCredits += cost
                    if section.sectionName not in selectedNames:
                        selected.append(i18n.makeString('#menu:customization/change/{0:>s}'.format(section.sectionName)))
                        selectedNames.append(section.sectionName)
                        removeStr = interface.getCurrentItemRemoveStr()
                    if removeStr is not None:
                        remove.extend(removeStr)
                else:
                    notSelected.append(i18n.makeString('#menu:customization/items/{0:>s}'.format(section.sectionName)))
            else:
                LOG_ERROR('Section not found', section.sectionName)

        if len(notSelected) > 0:
            DialogsInterface.showI18nInfoDialog('customization/selectNewItems', lambda success: None, I18nInfoDialogMeta('customization/selectNewItems', messageCtx={'items': ', '.join(notSelected)}))
            yield lambda callback = None: callback
        if totalGold or totalCredits:
            titleKey = DIALOGS.CUSTOMIZATION_CHANGECONFIRMATION_BUY
        else:
            titleKey = DIALOGS.CUSTOMIZATION_CHANGECONFIRMATION_CHANGE
        isConfirmed = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/changeConfirmation', titleCtx={'action': i18n.makeString(titleKey)}, messageCtx={'selected': ', '.join(selected),
         'remove': '\n'.join(remove)}))
        if isConfirmed:
            creditsNotEnough = totalCredits > self.__credits
            goldNotEnough = totalGold > self.__gold
            if creditsNotEnough or goldNotEnough:
                if creditsNotEnough and goldNotEnough:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_CREDITS_AND_GOLD_NOT_ENOUGH
                elif goldNotEnough:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_GOLD_NOT_ENOUGH
                else:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_CREDITS_NOT_ENOUGH
                SystemMessages.pushI18nMessage(key, type=SystemMessages.SM_TYPE.Error)
                yield lambda callback = None: callback
            self.__returnHangar = True
            vehInvID = g_currentVehicle.invID
            self.__steps = 0
            self.__messages = []
            self.flashObject.applyButton.disabled = True
            if len(sections) > 0:
                Waiting.show('customizationApply')
                self.__lockUpdate = True
            selectedNames = []
            for section in sections:
                interface = self.__interfaces.get(section.sectionName)
                if interface is not None:
                    newItems = interface.getNewItems()
                    if newItems is not None:
                        hasMatches = self.__hasNewItemsDuplicates(newItemsByType, newItems, interface._type)
                        self.__steps += interface.getSelectedItemsCount(section.isGold)
                        if section.sectionName not in selectedNames:
                            interface.change(vehInvID, section, hasMatches)
                            selectedNames.append(section.sectionName)
                else:
                    LOG_ERROR('Change operation, section not found', section)
                    self.__steps -= 1

            if not self.__steps:
                self.__onServerResponsesReceived()
        return

    def __updateNewItemsByType(self, newItemsByType, newItems, interfaceType):
        byType = newItemsByType[interfaceType]
        if newItems is not None:

            def matcher(x, y):
                return x['id'] == y['id'] and x['price']['isGold'] == y['price']['isGold'] and x['price']['isGold']

            for i in newItems:
                if i['price']['isGold'] and not findFirst(partial(matcher, i), byType, False):
                    byType.append(i)

        return

    def __hasNewItemsDuplicates(self, newItemsByType, newItems, interfaceType):
        matches = []
        if newItems is not None and interfaceType in newItemsByType:
            matches = [ i for i in newItemsByType[interfaceType] for j in newItems if i['id'] == j['id'] and i != j ]
        return len(matches) > 0

    @process
    def dropCurrentItemInSection(self, section, kind):
        self.__isIgrChanged = False
        if g_currentVehicle.isLocked():
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_VEHICLE_LOCKED, type=SystemMessages.SM_TYPE.Error)
            return
        elif g_currentVehicle.isBroken():
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.customization_vehicle(g_currentVehicle.item.getState()), type=SystemMessages.SM_TYPE.Error)
            return
        else:
            interface = self.__interfaces.get(section)
            if interface is not None:
                dialog = interface.getDrorStr(section, kind)
                isConfirmed = yield DialogsInterface.showI18nConfirmDialog(dialog)
                if self.__isIgrChanged:
                    SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_IGR_TYPE_CHANGED_ERROR, type=SystemMessages.SM_TYPE.Error)
                    self.__isIgrChanged = False
                elif isConfirmed:
                    self.__returnHangar = False
                    self.__lockUpdate = True
                    Waiting.show('customizationDrop')
                    interface.drop(g_currentVehicle.invID, kind)
            else:
                LOG_ERROR('Drop operation, section not found', section)
            return
