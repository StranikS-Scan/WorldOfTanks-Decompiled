# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/InscriptionInterface.py
import BigWorld
from abc import abstractmethod, ABCMeta
from CurrentVehicle import g_currentVehicle
from constants import IGR_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
import gui
from gui.Scaleform.daapi.view.lobby.customization.BaseTimedCustomizationInterface import BaseTimedCustomizationInterface
from gui.Scaleform.daapi.view.lobby.customization.VehicleCustonizationModel import VehicleCustomizationModel
from gui.Scaleform.daapi.view.lobby.customization.data_providers import InscriptionDataProvider, InscriptionRentalPackageDataProvider, InscriptionGroupsDataProvider
from gui.Scaleform.daapi.view.lobby.customization import CustomizationHelper
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.game_control import getRoamingCtrl
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.LobbyContext import g_lobbyContext
from helpers import time_utils, i18n
from items import vehicles

class InscriptionInterface(BaseTimedCustomizationInterface):
    __metaclass__ = ABCMeta

    def __init__(self, name, nationId, type, position):
        super(InscriptionInterface, self).__init__(name, nationId, type, position)
        self._isEnabled = False
        self._vehicleLevel = 1

    def __del__(self):
        LOG_DEBUG('InscriptionInterface deleted')

    def getCurrentItem(self):
        self.locateCameraOnSlot()
        return super(InscriptionInterface, self).getCurrentItem()

    def isEnabled(self):
        serverSettigns = g_lobbyContext.getServerSettings()
        if serverSettigns is not None and serverSettigns.roaming.isInRoaming():
            return False
        else:
            return self._isEnabled

    def locateCameraOnSlot(self):
        res = g_hangarSpace.space.locateCameraOnEmblem(not self.isTurret, 'inscription', self._position - self._positionShift, self.ZOOM_FACTOR)

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

    def isNewItemIGR(self):
        return self._itemsDP.isIGRItem(self._newItemID)

    def getItemDefaultPriceFactor(self, vehType):
        return self._vehicleLevel

    def updateVehicleCustomization(self, itemID = None):
        space = g_hangarSpace.space
        if space is not None and g_currentVehicle.isInHangar():
            VehicleCustomizationModel.updateVehicleSticker('inscription', itemID, self.getRealPosition(), self._rentalPackageDP.selectedPackage.get('periodDays'))
            space.updateVehicleSticker(VehicleCustomizationModel.getVehicleModel())
        return

    def updateSlotsPosition(self, vehDescr):
        if vehDescr is not None:
            self._vehicleLevel = vehDescr.type.level
            slotsCount = self.getSlotsCount(vehDescr.turret, 'inscription')
            self.isTurret = slotsCount > self._position
            if self._position == 1 and slotsCount == 1:
                self._positionShift = 1
            if not self.isTurret:
                slotsCount += self.getSlotsCount(vehDescr.hull, 'inscription')
            self._isEnabled = slotsCount > self._position
        return

    def fetchCurrentItem(self, vehDescr):
        if vehDescr is not None:
            self.updateSlotsPosition(vehDescr)
            inscription = vehDescr.playerInscriptions[self.getRealPosition()]
            if inscription is not None and inscription[0] is not None:
                self._currentItemID, startTime, days, _ = inscription
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
        return

    def change(self, vehInvID, section, isAlreadyPurchased):
        if self._newItemID is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_NOT_SELECTED)
            self.onCustomizationChangeFailed(message)
            return
        elif self._rentalPackageDP.selectedPackage is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_DAYS_NOT_SELECTED)
            self.onCustomizationChangeFailed(message)
            return
        else:
            cost, isGold = self._itemsDP.getCost(self._newItemID)
            if cost < 0:
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_COST_NOT_FOUND)
                self.onCustomizationChangeFailed(message)
                return
            if isAlreadyPurchased:
                daysToWear = 0
                cost = 0
            elif CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, self._newItemID, self._nationID, self._itemsDP.position):
                hangarItem = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, self._newItemID, self._nationID, self._itemsDP.position)
                daysToWear = 0 if hangarItem.get('isPermanent') else 7
            else:
                daysToWear = self._rentalPackageDP.selectedPackage.get('periodDays')
            newIdToSend = 0
            isNewInDefaultSetup = False
            isCurrIgr = self._itemsDP.isIGRItem(self._currentItemID)
            if isCurrIgr:
                isNewInDefaultSetup = CustomizationHelper.isIdInDefaultSetup(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, self._newItemID)
            if self._currentItemID is None or not isCurrIgr or isCurrIgr and not isNewInDefaultSetup or isCurrIgr and isNewInDefaultSetup and daysToWear > 0:
                newIdToSend = self._newItemID
            BigWorld.player().inventory.changeVehicleInscription(vehInvID, self.getRealPosition(), newIdToSend, daysToWear, 1, lambda resultID: self.__onChangeVehicleInscription(resultID, (cost, isGold)))
            return

    def drop(self, vehInvID, kind):
        if self._currentItemID is None:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_NOT_FOUND_TO_DROP)
            self.onCustomizationDropFailed(message)
            return
        else:
            BigWorld.player().inventory.changeVehicleInscription(vehInvID, self.getRealPosition(), 0, 0, 1, self.__onDropVehicleInscription)
            return

    def update(self, vehicleDescr):
        inscription = vehicleDescr.playerInscriptions[self.getRealPosition()]
        inscriptionID = inscription[0] if inscription is not None else None
        if inscriptionID != self._currentItemID:
            self._currentItemID = inscriptionID
            self._itemsDP.currentItemID = self._currentItemID
            if inscription is not None:
                _, startTime, days, colorId = inscription
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
            else:
                self._currentLifeCycle = None
            self.onCurrentItemChange(self._name)
        return

    def _populate(self):
        super(InscriptionInterface, self)._populate()

    def _dispose(self):
        super(InscriptionInterface, self)._dispose()

    def __onChangeVehicleInscription(self, resultID, price):
        if resultID < 0:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SERVER_ERROR)
            self.onCustomizationChangeFailed(message)
            return
        else:
            self._currentItemID = self._newItemID
            self._currentLifeCycle = None
            self._newItemID = None
            self._itemsDP.currentItemID = self._currentItemID
            cost, isGold = price
            if cost == 0:
                key = SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_FREE
                type = SystemMessages.SM_TYPE.Information
                str = i18n.makeString(key)
            else:
                if isGold:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_GOLD
                    fCost = BigWorld.wg_getGoldFormat(cost)
                    type = SystemMessages.SM_TYPE.CustomizationForGold
                else:
                    key = SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_CHANGE_SUCCESS_CREDITS
                    fCost = BigWorld.wg_getIntegralFormat(cost)
                    type = SystemMessages.SM_TYPE.CustomizationForCredits
                str = i18n.makeString(key, fCost)
            self.onCustomizationChangeSuccess(str, type)
            return

    def __onDropVehicleInscription(self, resultID):
        if resultID < 0:
            message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_DROP_SERVER_ERROR)
            self.onCustomizationDropFailed(message)
            return
        else:
            newID = None
            newLifeCycle = None
            if gui.game_control.g_instance.igr.getRoomType() != IGR_TYPE.NONE:
                inscriptions = g_currentVehicle.item.descriptor.playerInscriptions
                inscr = inscriptions[self.getRealPosition()]
                if inscr[0] is not None:
                    newID = inscr[0]
                    newLifeCycle = (inscr[1], inscr[2])
            hangarItem = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, self._currentItemID, self._nationID)
            if hangarItem:
                intCD = g_currentVehicle.item.intCD
                vehicle = vehicles.getVehicleType(int(intCD))
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_STORED_SUCCESS, vehicle=vehicle.userString)
            else:
                message = i18n.makeString(SYSTEM_MESSAGES.CUSTOMIZATION_INSCRIPTION_DROP_SUCCESS)
            self._currentItemID = newID
            self._currentLifeCycle = newLifeCycle
            self._itemsDP.currentItemID = newID
            self.updateVehicleCustomization(newID)
            self.onCustomizationDropSuccess(message)
            return


class InscriptionLeftInterface(InscriptionInterface):

    def getItemsDP(self):
        dp = InscriptionDataProvider(self._nationID, self.getRealPosition())
        dp.setFlashObject(self.flashObject.inscriptionLeftDP)
        return dp

    def getRentalPackagesDP(self):
        dp = InscriptionRentalPackageDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.inscriptionLeftRentalPackageDP)
        return dp

    def getGroupsDP(self):
        dp = InscriptionGroupsDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.inscriptionLeftGroupsDataProvider)
        return dp


class InscriptionRightInterface(InscriptionInterface):

    def getItemsDP(self):
        dp = InscriptionDataProvider(self._nationID, self.getRealPosition())
        dp.setFlashObject(self.flashObject.inscriptionRightDP)
        return dp

    def getRentalPackagesDP(self):
        dp = InscriptionRentalPackageDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.inscriptionRightRentalPackageDP)
        return dp

    def getGroupsDP(self):
        dp = InscriptionGroupsDataProvider(self._nationID)
        dp.setFlashObject(self.flashObject.inscriptionRightGroupsDataProvider)
        return dp
