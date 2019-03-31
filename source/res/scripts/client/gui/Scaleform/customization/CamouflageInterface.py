# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/CamouflageInterface.py
# Compiled at: 2011-12-20 18:23:08
import BigWorld
from datetime import timedelta
from math import ceil
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.customization.CustomizationInterface import CustomizationInterface
from gui.Scaleform.customization.data_providers import CamouflageGroupsDataProvider, CamouflagesDataProvider, CamouflageRentalPackageDataProvider
from gui.Scaleform.utils.HangarSpace import g_hangarSpace
from helpers import i18n, time_utils
import time

class CamouflageInterface(CustomizationInterface):

    def __init__(self, name):
        super(CamouflageInterface, self).__init__(name)
        self._nationID = None
        self._currentCamouflageID = None
        self._currentLifeCycle = None
        self._newCamouflageID = None
        self._selectedPeriodDays = None
        return

    def __del__(self):
        LOG_DEBUG('CamouflageInterface deleted')

    def __updateVehicleCamouflage(self, camouflageID=None):
        space = g_hangarSpace.space
        if space is not None and g_currentVehicle.isInHangar():
            space.updateVehicleCamouflage(camouflageID=camouflageID)
        return

    def __makeTimeLeftString(self):
        if self._currentLifeCycle is None:
            return ''
        else:
            startTime, days = self._currentLifeCycle
            result = ''
            if days > 0:
                timeLeft = startTime + days * 86400 - time.time()
                if timeLeft > 0:
                    delta = timedelta(0, timeLeft)
                    if delta.days > 0:
                        result = i18n.makeString('#menu:customization/labels/timeLeft/days', delta.days + 1 if delta.seconds > 0 else delta.days)
                    else:
                        result = i18n.makeString('#menu:customization/labels/timeLeft/hours', ceil(delta.seconds / 3600.0))
            return result

    def populateUI(self, proxy):
        super(CamouflageInterface, self).populateUI(proxy)
        self.uiHolder.addExternalCallbacks({'Customization.Vehicle.Camouflage.RequestCurrent': self.onRequestCurrentCamouflage,
         'Customization.Vehicle.Camouflage.GetSelectedPeriodDays': self.onGetSelectedPeriodDays,
         'Customization.Vehicle.Camouflage.SetPeriodDays': self.onSelectPeriodDays,
         'Customization.Vehicle.Camouflage.SetCamouflageID': self.onSetCamouflageID})
        self._rentalPackageDP = CamouflageRentalPackageDataProvider('Customization.Vehicle.Camouflage.RentalPackage')
        self._groupsDP = CamouflageGroupsDataProvider('Customization.Vehicle.Camouflage.Groups')
        self._selectedGroupDP = CamouflagesDataProvider('Customization.Vehicle.Camouflage.SelectedGroup')
        self._rentalPackageDP.populateUI(proxy)
        self._groupsDP.populateUI(proxy)
        self._selectedGroupDP.populateUI(proxy)

    def dispossessUI(self):
        if self._newCamouflageID is not None:
            self.__updateVehicleCamouflage()
        self.uiHolder.removeExternalCallbacks('Customization.Vehicle.Camouflage.RequestCurrent', 'Customization.Vehicle.Camouflage.GetSelectedPeriodDays', 'Customization.Vehicle.Camouflage.SetPeriodDays', 'Customization.Vehicle.Camouflage.SetCamouflageID')
        self._rentalPackageDP.dispossessUI()
        self._groupsDP.dispossessUI()
        self._selectedGroupDP.dispossessUI()
        self._rentalPackageDP = None
        self._groupsDP = None
        self._selectedGroupDP = None
        self._eventManager.clear()
        super(CamouflageInterface, self).dispossessUI()
        return

    def fetchCurrentItem(self, vehDescr):
        if vehDescr is not None:
            self._nationID = vehDescr.type.id[0]
            camouflage = vehDescr.camouflage
            if camouflage is not None:
                self._currentCamouflageID, startTime, days = camouflage
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
        return

    def invalidateData(self, vehType, refresh=False):
        if vehType is not None:
            self._groupsDP.buildList(self._nationID)
            self._selectedGroupDP.setVehicleTypeParams(vehType.camouflagePriceFactor, self._currentCamouflageID)
        BigWorld.player().shop.getCamouflageCost(lambda resultID, costs, rev: self.__onGetCamouflageCost(resultID, costs, rev, refresh))
        return

    def isNewItemSelected(self):
        return self._newCamouflageID is not None

    def getSelectedItemCost(self):
        return self._selectedGroupDP.getCost(self._nationID, self._newCamouflageID)

    def isCurrentItemRemove(self):
        return self._currentCamouflageID is not None

    def change(self, vehInvID):
        if self._newCamouflageID is None:
            message = i18n.makeString('#system_messages:customization/camouflage_not_selected')
            self.onCustomizationChangeFailed(message)
            return
        elif self._selectedPeriodDays is None:
            message = i18n.makeString('#system_messages:customization/camouflage_days_not_selected')
            self.onCustomizationChangeFailed(message)
            return
        else:
            cost, isGold = self._selectedGroupDP.getCost(self._nationID, self._newCamouflageID)
            if cost < 0:
                message = i18n.makeString('#system_messages:customization/camouflage_cost_not_found')
                self.onCustomizationChangeFailed(message)
                return
            BigWorld.player().inventory.changeVehicleCamouflage(vehInvID, self._newCamouflageID, self._selectedPeriodDays, lambda resultID: self.__onChangeVehicleCamouflage(resultID, (cost, isGold)))
            return

    def drop(self, vehInvID):
        if self._currentCamouflageID is None:
            message = i18n.makeString('#system_messages:customization/camouflage_not_found_to_drop')
            self.onCustomizationDropFailed(message)
            return
        else:
            BigWorld.player().inventory.changeVehicleCamouflage(vehInvID, 0, 0, self.__onDropVehicleCamouflage)
            return

    def update(self, vehicleDescr):
        camouflage = vehicleDescr.camouflage
        camouflageID = camouflage[0] if camouflage is not None else None
        if camouflageID != self._currentCamouflageID:
            self._currentCamouflageID = camouflageID
            self._selectedGroupDP.currentCamouflageID = self._currentCamouflageID
            if camouflage is not None:
                _, startTime, days = camouflage
                startTime = time_utils.makeLocalServerTime(startTime)
                self._currentLifeCycle = (startTime, days)
            else:
                self._currentLifeCycle = None
            self.call('Customization.Vehicle.Camouflage.CurrentChanged')
        return

    def __onGetCamouflageCost(self, resultID, costs, _, refresh):
        if resultID < 0:
            SystemMessages.pushI18nMessage('#system_messages:customization/camouflage_get_cost_server_error', type=SystemMessages.SM_TYPE.Error)
        else:
            self._rentalPackageDP.buildList(costs)
            packageIdx = self._rentalPackageDP.DEFAULT_RENTAL_PACKAGE_IDX
            if self._selectedPeriodDays is not None:
                packageIdx = self._rentalPackageDP.getIndexByDays(self._selectedPeriodDays)
            periodDays, cost, isGold, _ = self._rentalPackageDP.requestItemAt(packageIdx)
            assert cost > -1
            self._selectedPeriodDays = periodDays
            self._selectedGroupDP.setDefaultCost(cost, isGold)
        if refresh:
            self._newCamouflageID = None
            self._rentalPackageDP.refresh()
            self._selectedGroupDP.refresh()
        LOG_DEBUG('CamouflageInterface data inited.')
        self.onDataInited(self._name)
        return

    def __onChangeVehicleCamouflage(self, resultID, price):
        if resultID < 0:
            message = i18n.makeString('#system_messages:customization/camouflage_change_server_error')
            self.onCustomizationChangeFailed(message)
            return
        else:
            self._currentCamouflageID = self._newCamouflageID
            self._currentLifeCycle = None
            self._newCamouflageID = None
            self._selectedGroupDP.currentCamouflageID = self._currentCamouflageID
            self.call('Customization.Vehicle.Camouflage.ChangeSuccess')
            cost, isGold = price
            if isGold:
                key = '#system_messages:customization/camouflage_change_success/gold'
                fCost = BigWorld.wg_getGoldFormat(cost)
                type = SystemMessages.SM_TYPE.CustomizationForGold
            else:
                key = '#system_messages:customization/camouflage_change_success/credits'
                fCost = BigWorld.wg_getIntegralFormat(cost)
                type = SystemMessages.SM_TYPE.CustomizationForCredits
            self.onCustomizationChangeSuccess(i18n.makeString(key, fCost), type)
            return

    def __onDropVehicleCamouflage(self, resultID):
        if resultID < 0:
            message = i18n.makeString('#system_messages:customization/camouflage_drop_server_error')
            self.onCustomizationDropFailed(message)
            return
        else:
            self._currentCamouflageID = None
            self._currentLifeCycle = None
            self._selectedGroupDP.currentCamouflageID = None
            if self._newCamouflageID is None:
                g_currentVehicle.update()
            self.call('Customization.Vehicle.Camouflage.DropSuccess')
            message = i18n.makeString('#system_messages:customization/camouflage_drop_success')
            self.onCustomizationDropSuccess(message)
            return

    def onRequestCurrentCamouflage(self, *args):
        parser = CommandArgsParser(self.onRequestCurrentCamouflage.__name__)
        parser.parse(*args)
        camouflageInfo = self._selectedGroupDP.makeItem(self._nationID, self._currentCamouflageID, False, lifeCycle=self._currentLifeCycle)
        camouflageInfo.insert(0, self._nationID)
        camouflageInfo.insert(1, self.__makeTimeLeftString())
        parser.addArgs(camouflageInfo)
        self.respond(parser.args())

    def onSetCamouflageID(self, *args):
        parser = CommandArgsParser(self.onSetCamouflageID.__name__, 1, [int])
        camouflageID = parser.parse(*args)
        if self._currentCamouflageID == camouflageID:
            self._newCamouflageID = None
        else:
            self._newCamouflageID = camouflageID
        self.__updateVehicleCamouflage(camouflageID)
        return

    def onGetSelectedPeriodDays(self, *args):
        parser = CommandArgsParser(self.onGetSelectedPeriodDays.__name__)
        parser.parse(*args)
        parser.addArg(self._rentalPackageDP.getIndexByDays(self._selectedPeriodDays))
        self.respond(parser.args())

    def onSelectPeriodDays(self, *args):
        parser = CommandArgsParser(self.onSelectPeriodDays.__name__, 1, [int])
        idx = parser.parse(*args)
        periodDays, cost, isGold, _ = self._rentalPackageDP.requestItemAt(idx)
        assert cost > -1
        self._selectedPeriodDays = periodDays
        self._selectedGroupDP.setDefaultCost(cost, isGold)
        parser.addArg(self._nationID)
        self.respond(parser.args())
