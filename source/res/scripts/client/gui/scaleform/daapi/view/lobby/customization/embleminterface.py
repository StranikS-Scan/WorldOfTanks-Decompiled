# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/EmblemInterface.py
import BigWorld
from abc import abstractmethod, ABCMeta
import time
from CurrentVehicle import g_currentVehicle
from constants import IGR_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
import gui
from gui.Scaleform.daapi.view.lobby.customization.BaseTimedCustomizationInterface import BaseTimedCustomizationInterface
from gui.Scaleform.daapi.view.lobby.customization.VehicleCustonizationModel import VehicleCustomizationModel
from gui.Scaleform.daapi.view.lobby.customization.data_providers import EmblemsDataProvider, EmblemRentalPackageDataProvider, EmblemGroupsDataProvider
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.utils.HangarSpace import g_hangarSpace
from helpers import time_utils, i18n
from gui.Scaleform.daapi.view.lobby.customization import CustomizationHelper
from items import vehicles
from gui.LobbyContext import g_lobbyContext

class EmblemInterface(BaseTimedCustomizationInterface):
    __metaclass__ = ABCMeta

    def __init__(self, name, nationId, type, position):
        super(EmblemInterface, self).__init__(name, nationId, type, position)
        self.defaultPlayerEmblemID = None
        self._isEnabled = False
        self._vehicleLevel = 1
        self._positionShift = 0
        return

    def __del__(self):
        LOG_DEBUG('EmblemInterface deleted')

    def getCurrentItem(self):
        self.locateCameraOnSlot()
        item = super(EmblemInterface, self).getCurrentItem()
        if self.defaultPlayerEmblemID == item.get('id'):
            item['canDrop'] = False
        return item

    def isEnabled(self):
        serverSettings = g_lobbyContext.getServerSettings()
        if serverSettings is not None and serverSettings.roaming.isInRoaming():
            return False
        else:
            return self._isEnabled

    def locateCameraOnSlot(self):
        res = g_hangarSpace.space.locateCameraOnEmblem(not self.isTurret, 'player', self._position - self._positionShift, self.ZOOM_FACTOR)
        LOG_DEBUG('EmblemLeftInterface g_hangarSpace.space.locateCameraOnEmblem', self._position, res)

    @abstractmethod
    def getRentalPackagesDP(self):
        pass

    @abstractmethod
    def getGroupsDP(self):
        pass

    @abstractmethod
    def getItemsDP(self):
        pass

    def getItemPriceFactor(self, vehType):
        return self._vehicleLevel

    def getItemDefaultPriceFactor(self, vehType):
        return self._vehicleLevel

    def isNewItemIGR(self):
        return self._itemsDP.isIGRItem(self._newItemID)

    def updateVehicleCustomization(self, itemID = None):
        space = g_hangarSpace.space
        if space is not None and g_currentVehicle.isInHangar():
            VehicleCustomizationModel.updateVehicleSticker('player', itemID, self.getRealPosition(), self._rentalPackageDP.selectedPackage.get('periodDays'))
            space.updateVehicleSticker(VehicleCustomizationModel.getVehicleModel())
        return

    def updateSlotsPosition(self, vehDescr):
        if vehDescr is not None:
            self._vehicleLevel = vehDescr.type.level
            slotsCount = self.getSlotsCount(vehDescr.turret, 'player')
            self.isTurret = slotsCount > self._position
            if self._position == 1 and slotsCount == 1:
                self._positionShift = 1
            if not self.isTurret:
                slotsCount += self.getSlotsCount(vehDescr.hull, 'player')
            self._isEnabled = slotsCount > self._position
        return

    def fetchCurrentItem(self, vehDescr):
        if vehDescr is not None:
            self.updateSlotsPosition(vehDescr)
            self.defaultPlayerEmblemID = vehDescr.type.defaultPlayerEmblemID
            emblem = vehDescr.playerEmblems[self.getRealPosition()]
            if emblem is not None:
                self._currentItemID, startTime, days = emblem
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
        return

    def change(self, vehInvID, section, isAlreadyPurchased):
        if self._newItemID is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_NOT_SELECTED)
            self.onCustomizationChangeFailed(message)
            return
        elif self._rentalPackageDP.selectedPackage is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_DAYS_NOT_SELECTED)
            self.onCustomizationChangeFailed(message)
            return
        else:
            cost, isGold = self._itemsDP.getCost(self._newItemID)
            if cost < 0:
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_COST_NOT_FOUND)
                self.onCustomizationChangeFailed(message)
                return
            if isAlreadyPurchased:
                daysToWear = 0
                cost = 0
            elif CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, self._newItemID, self._nationID, self._itemsDP.position):
                hangarItem = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE, self._newItemID, self._nationID, self._itemsDP.position)
                daysToWear = 0 if hangarItem.get('isPermanent') else 7
            else:
                daysToWear = self._rentalPackageDP.selectedPackage.get('periodDays')
            newIdToSend = 0
            isNewInDefaultSetup = False
            isCurrIgr = self._itemsDP.isIGRItem(self._currentItemID)
            if isCurrIgr:
                isNewInDefaultSetup = CustomizationHelper.isIdInDefaultSetup(CUSTOMIZATION_ITEM_TYPE.EMBLEM, self._newItemID)
            if self._currentItemID is None or not isCurrIgr or isCurrIgr and not isNewInDefaultSetup or isCurrIgr and isNewInDefaultSetup and daysToWear > 0:
                newIdToSend = self._newItemID
            BigWorld.player().inventory.changeVehicleEmblem(vehInvID, self.getRealPosition(), newIdToSend, daysToWear, lambda resultID: self.__onChangeVehicleEmblem(resultID, (cost, isGold)))
            return

    def drop(self, vehInvID, kind):
        if self._currentItemID is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_NOT_FOUND_TO_DROP)
            self.onCustomizationDropFailed(message)
            return
        else:
            BigWorld.player().inventory.changeVehicleEmblem(vehInvID, self.getRealPosition(), 0, 0, self.__onDropVehicleEmblem)
            return

    def update(self, vehicleDescr):
        emblem = vehicleDescr.playerEmblems[self.getRealPosition()]
        emblemID = emblem[0] if emblem is not None else None
        if emblemID != self._currentItemID:
            self._currentItemID = emblemID
            self._itemsDP.currentItemID = self._currentItemID
            if emblem is not None:
                _, startTime, days = emblem
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
            else:
                self._currentLifeCycle = None
            self.onCurrentItemChange(self._name)
        return

    def _populate(self):
        super(EmblemInterface, self)._populate()

    def _dispose(self):
        super(EmblemInterface, self)._dispose()

    def __onChangeVehicleEmblem(self, resultID, price):
        if resultID < 0:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SERVER_ERROR)
            self.onCustomizationChangeFailed(message)
            return
        else:
            self._currentItemID = self._newItemID
            self._currentLifeCycle = (round(time.time()), 0)
            self._newItemID = None
            self._itemsDP.currentItemID = self._currentItemID
            cost, isGold = price
            if cost == 0:
                key = SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_FREE
                type = SystemMessages.SM_TYPE.Information
                str = i18n.makeString(key)
            else:
                if isGold:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_GOLD
                    fCost = BigWorld.wg_getGoldFormat(cost)
                    type = SystemMessages.SM_TYPE.CustomizationForGold
                else:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_CHANGE_SUCCESS_CREDITS
                    fCost = BigWorld.wg_getIntegralFormat(cost)
                    type = SystemMessages.SM_TYPE.CustomizationForCredits
                str = i18n.makeString(key, fCost)
            self.onCustomizationChangeSuccess(str, type)
            return

    def __onDropVehicleEmblem(self, resultID):
        if resultID < 0:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_DROP_SERVER_ERROR)
            self.onCustomizationDropFailed(message)
            return
        else:
            newID = self.defaultPlayerEmblemID
            newLifeCycle = None
            if gui.game_control.g_instance.igr.getRoomType() != IGR_TYPE.NONE:
                emblems = g_currentVehicle.item.descriptor.playerEmblems
                emblem = emblems[self.getRealPosition()]
                if emblem[0] is not None:
                    newID = emblem[0]
                    newLifeCycle = (emblem[1], emblem[2])
            hangarItem = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE, self._currentItemID, self._nationID)
            if hangarItem:
                intCD = g_currentVehicle.item.intCD
                vehicle = vehicles.getVehicleType(int(intCD))
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_STORED_SUCCESS, vehicle=vehicle.userString)
            else:
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_EMBLEM_DROP_SUCCESS)
            self._currentItemID = newID
            self._currentLifeCycle = newLifeCycle
            self._itemsDP.currentItemID = newID
            self.updateVehicleCustomization(newID)
            self.onCustomizationDropSuccess(message)
            self.onCurrentItemChange(self._name)
            return


class EmblemLeftInterface(EmblemInterface):

    def getItemsDP(self):
        dp = EmblemsDataProvider(self._nationID, self.getRealPosition())
        dp.setFlashObject(self.flashObject.emblemLeftDP)
        return dp

    def getRentalPackagesDP(self):
        dp = EmblemRentalPackageDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.emblemLeftRentalPackageDP)
        return dp

    def getGroupsDP(self):
        dp = EmblemGroupsDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.emblemLeftGroupsDataProvider)
        return dp


class EmblemRightInterface(EmblemInterface):

    def getItemsDP(self):
        dp = EmblemsDataProvider(self._nationID, self.getRealPosition())
        dp.setFlashObject(self.flashObject.emblemRightDP)
        return dp

    def getRentalPackagesDP(self):
        dp = EmblemRentalPackageDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.emblemRightRentalPackageDP)
        return dp

    def getGroupsDP(self):
        dp = EmblemGroupsDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.emblemRightGroupsDataProvider)
        return dp
