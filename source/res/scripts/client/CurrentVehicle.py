# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CurrentVehicle.py
import BigWorld
from constants import CustomizationInvData
from Event import Event, EventManager
from adisp import process
from gui.shared.formatters.time_formatters import getTimeLeftStr
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from gui.vehicle_view_states import createState4CurrentVehicle
from helpers import dependency
from items.vehicles import VehicleDescr
from helpers import isPlayerAccount, i18n
from account_helpers.AccountSettings import AccountSettings, CURRENT_VEHICLE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.formatters import icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.Waiting import Waiting
from skeletons.gui.game_control import IIGRController, IRentalsController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_MODULES_NAMES = ('turret',
 'chassis',
 'engine',
 'gun',
 'radio')

class _CachedVehicle(object):
    itemsCache = dependency.descriptor(IItemsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self._eManager = EventManager()
        self.onChanged = Event(self._eManager)
        self.onChangeStarted = Event(self._eManager)
        self.__changeCallbackID = None
        return

    def init(self):
        self._addListeners()

    def destroy(self):
        self._eManager.clear()
        self._clearChangeCallback()
        self._removeListeners()

    def selectVehicle(self, vehID):
        raise NotImplementedError

    def selectNoVehicle(self):
        raise NotImplementedError

    def isPresent(self):
        return self.item is not None

    def onInventoryUpdate(self, invDiff):
        raise NotImplementedError

    def refreshModel(self):
        raise NotImplementedError

    @property
    def item(self):
        raise NotImplementedError

    @property
    def invID(self):
        raise NotImplementedError

    def _addListeners(self):
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _changeDone(self):
        self._clearChangeCallback()
        if isPlayerAccount():
            self.onChanged()
        Waiting.hide('updateCurrentVehicle')

    def _setChangeCallback(self):
        if not self.__changeCallbackID:
            self.__changeCallbackID = BigWorld.callback(0.2, self._changeDone)

    def _clearChangeCallback(self):
        if self.__changeCallbackID is not None:
            BigWorld.cancelCallback(self.__changeCallbackID)
            self.__changeCallbackID = None
        return

    def _selectVehicle(self, vehID):
        raise NotImplementedError


class _CurrentVehicle(_CachedVehicle):
    igrCtrl = dependency.descriptor(IIGRController)
    rentals = dependency.descriptor(IRentalsController)

    def __init__(self):
        super(_CurrentVehicle, self).__init__()
        self.__vehInvID = 0

    def init(self):
        super(_CurrentVehicle, self).init()
        prbVehicle = self.__checkPrebattleLockedVehicle()
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        self.selectVehicle(prbVehicle or storedVehInvID)

    def destroy(self):
        super(_CurrentVehicle, self).destroy()
        self.__vehInvID = 0
        self.hangarSpace.removeVehicle()
        self.selectNoVehicle()

    def onIgrTypeChanged(self, *args):
        if self.isPremiumIGR():
            self.onChanged()
        self.refreshModel()

    def onRentChange(self, vehicles):
        if self.isPresent():
            if self.item.intCD in vehicles:
                self.onChanged()

    def onInventoryUpdate(self, invDiff):
        vehsDiff = invDiff.get(GUI_ITEM_TYPE.VEHICLE, {})
        isVehicleSold = False
        isVehicleDescrChanged = False
        if 'compDescr' in vehsDiff and self.__vehInvID in vehsDiff['compDescr']:
            isVehicleSold = vehsDiff['compDescr'][self.__vehInvID] is None
            isVehicleDescrChanged = not isVehicleSold
        if isVehicleSold or self.__vehInvID == 0:
            self.selectVehicle()
        else:
            isRepaired = 'repair' in vehsDiff and self.__vehInvID in vehsDiff['repair']
            isCustomizationChanged = CustomizationInvData.OUTFITS in invDiff.get(GUI_ITEM_TYPE.CUSTOMIZATION, {})
            isComponentsChanged = GUI_ITEM_TYPE.TURRET in invDiff or GUI_ITEM_TYPE.GUN in invDiff
            isVehicleChanged = any((self.__vehInvID in hive or (self.__vehInvID, '_r') in hive for hive in vehsDiff.itervalues()))
            if isComponentsChanged or isRepaired or isVehicleDescrChanged or isCustomizationChanged:
                self.refreshModel()
            if isVehicleChanged or isRepaired:
                self.onChanged()
        return

    def onRotationUpdate(self, diff):
        isVehicleChanged = False
        if 'groupBattles' in diff:
            isVehicleChanged = self.item.rotationGroupIdx in diff['groupBattles']
        elif 'isGroupLocked' in diff:
            isVehicleChanged = self.item.rotationGroupIdx in diff['isGroupLocked']
        if isVehicleChanged:
            self.onChanged()

    def onLocksUpdate(self, locksDiff):
        if self.__vehInvID in locksDiff:
            self.refreshModel()
            self.onChanged()

    def refreshModel(self):
        if g_currentPreviewVehicle.item is not None:
            return
        else:
            if self.isPresent() and self.isInHangar() and self.item.modelState:
                self.hangarSpace.startToUpdateVehicle(self.item)
            else:
                self.hangarSpace.removeVehicle()
            return

    @property
    def invID(self):
        return self.__vehInvID

    @property
    def item(self):
        return self.itemsCache.items.getVehicle(self.__vehInvID) if self.__vehInvID > 0 else None

    def isBroken(self):
        return self.isPresent() and self.item.isBroken

    def isGroupReady(self):
        return self.isPresent() and self.item.isGroupReady()[0]

    def isDisabledInRoaming(self):
        return self.isPresent() and self.item.isDisabledInRoaming

    def isLocked(self):
        return self.isPresent() and self.item.isLocked

    def isClanLock(self):
        return self.isPresent() and self.item.clanLock > 0

    def isCrewFull(self):
        return self.isPresent() and self.item.isCrewFull

    def isDisabledInRent(self):
        return self.isPresent() and self.item.rentalIsOver

    def isDisabledInPremIGR(self):
        return self.isPresent() and self.item.isDisabledInPremIGR

    def isRotationGroupLocked(self):
        return self.isPresent() and self.item.isRotationGroupLocked

    def isPremiumIGR(self):
        return self.isPresent() and self.item.isPremiumIGR

    def isInPrebattle(self):
        return self.isPresent() and self.item.isInPrebattle

    def isInBattle(self):
        return self.isPresent() and self.item.isInBattle

    def isInHangar(self):
        return self.isPresent() and not self.item.isInBattle

    def isAwaitingBattle(self):
        return self.isPresent() and self.item.isAwaitingBattle

    def isOnlyForEventBattles(self):
        return self.isPresent() and self.item.isOnlyForEventBattles

    def isOutfitLocked(self):
        return self.isPresent() and self.item.isOutfitLocked

    def isEvent(self):
        return self.isPresent() and self.item.isEvent

    def isObserver(self):
        return self.isPresent() and self.item.isObserver

    def isAlive(self):
        return self.isPresent() and self.item.isAlive

    def isReadyToPrebattle(self):
        return self.isPresent() and self.item.isReadyToPrebattle()

    def isReadyToFight(self):
        return self.isPresent() and self.item.isReadyToFight

    def isAutoLoadFull(self):
        return not self.isPresent() or self.item.isAutoLoadFull()

    def isAutoEquipFull(self):
        return not self.isPresent() or self.item.isAutoEquipFull()

    def selectVehicle(self, vehInvID=0):
        vehicle = self.itemsCache.items.getVehicle(vehInvID)
        if vehicle is None:
            invVehs = self.itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY)

            def notEvent(x, y):
                if x.isOnlyForEventBattles and not y.isOnlyForEventBattles:
                    return 1
                return -1 if not x.isOnlyForEventBattles and y.isOnlyForEventBattles else cmp(x, y)

            if invVehs:
                vehInvID = sorted(invVehs.itervalues(), cmp=notEvent)[0].invID
            else:
                vehInvID = 0
        self._selectVehicle(vehInvID)
        return

    def selectNoVehicle(self):
        self._selectVehicle(0)

    def getDossier(self):
        return self.itemsCache.items.getVehicleDossier(self.item.intCD)

    def getHangarMessage(self):
        if not self.isPresent():
            return (Vehicle.VEHICLE_STATE.NOT_PRESENT, MENU.CURRENTVEHICLESTATUS_NOTPRESENT, Vehicle.VEHICLE_STATE_LEVEL.CRITICAL)
        state, stateLvl = self.item.getState()
        if state == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
            icon = icons.premiumIgrBig()
            if self.item.isRented:
                rentLeftStr = getTimeLeftStr('#menu:vehicle/igrRentLeft/%s', self.item.rentInfo.getTimeLeft())
                message = i18n.makeString('#menu:currentVehicleStatus/' + state, icon=icon, time=rentLeftStr)
            else:
                message = i18n.makeString('#menu:tankCarousel/vehicleStates/inPremiumIgrOnly', icon=icon)
            return (state, message, stateLvl)
        message = '#menu:currentVehicleStatus/' + state
        return (state, message, stateLvl)

    def getViewState(self):
        return createState4CurrentVehicle(self)

    def _addListeners(self):
        super(_CurrentVehicle, self)._addListeners()
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.onLocksUpdate,
         'groupLocks': self.onRotationUpdate})
        self.igrCtrl.onIgrTypeChanged += self.onIgrTypeChanged
        self.rentals.onRentChangeNotify += self.onRentChange

    def _removeListeners(self):
        super(_CurrentVehicle, self)._removeListeners()
        self.igrCtrl.onIgrTypeChanged -= self.onIgrTypeChanged
        self.rentals.onRentChangeNotify -= self.onRentChange

    def _selectVehicle(self, vehInvID):
        if vehInvID == self.__vehInvID:
            return
        Waiting.show('updateCurrentVehicle', isSingle=True, overlapsUI=False)
        self.onChangeStarted()
        self.__vehInvID = vehInvID
        AccountSettings.setFavorites(CURRENT_VEHICLE, vehInvID)
        self.refreshModel()
        self._setChangeCallback()

    def __checkPrebattleLockedVehicle(self):
        from gui.prb_control import prb_getters
        clientPrb = prb_getters.getClientPrebattle()
        if clientPrb is not None:
            rosters = prb_getters.getPrebattleRosters(prebattle=clientPrb)
            for _, roster in rosters.iteritems():
                if BigWorld.player().id in roster:
                    vehCompDescr = roster[BigWorld.player().id].get('vehCompDescr', '')
                    if vehCompDescr:
                        vehDescr = VehicleDescr(vehCompDescr)
                        vehicle = self.itemsCache.items.getItemByCD(vehDescr.type.compactDescr)
                        if vehicle is not None:
                            return vehicle.invID

        return 0

    def __repr__(self):
        return 'CurrentVehicle(%s)' % str(self.item)


g_currentVehicle = _CurrentVehicle()

class PreviewAppearance(object):

    def refreshVehicle(self, item):
        raise NotImplementedError


class _RegularPreviewAppearance(PreviewAppearance):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def refreshVehicle(self, item):
        if item is not None:
            self.hangarSpace.updatePreviewVehicle(item)
        else:
            g_currentVehicle.refreshModel()
        return


class HeroTankPreviewAppearance(PreviewAppearance):

    def refreshVehicle(self, item):
        if item is None:
            from ClientSelectableCameraObject import ClientSelectableCameraObject
            ClientSelectableCameraObject.switchCamera()
        return


class _CurrentPreviewVehicle(_CachedVehicle):

    def __init__(self):
        super(_CurrentPreviewVehicle, self).__init__()
        self.__item = None
        self.__defaultItem = None
        self.__vehAppearance = _RegularPreviewAppearance()
        self.onComponentInstalled = Event(self._eManager)
        self.onVehicleUnlocked = Event(self._eManager)
        self.onVehicleInventoryChanged = Event(self._eManager)
        self.__vehAppearance = _RegularPreviewAppearance()
        return

    def destroy(self):
        super(_CurrentPreviewVehicle, self).destroy()
        self.__item = None
        self.__defaultItem = None
        self.__vehAppearance = None
        return

    def init(self):
        super(_CurrentPreviewVehicle, self).init()
        self.resetAppearance()

    def refreshModel(self):
        pass

    def selectVehicle(self, vehicleCD=None, vehicleStrCD=None):
        self._selectVehicle(vehicleCD, vehicleStrCD)

    def selectNoVehicle(self):
        self._selectVehicle(None)
        return

    def resetAppearance(self, appearance=None):
        self.__vehAppearance = appearance or _RegularPreviewAppearance()

    @property
    def item(self):
        return self.__item

    @property
    def defaultItem(self):
        return self.__defaultItem

    @property
    def invID(self):
        if self.isPresent():
            vehicle = self.itemsCache.items.getItemByCD(self.item.intCD)
            return vehicle.invID

    def onInventoryUpdate(self, invDiff):
        if self.isPresent():
            vehicle = self.itemsCache.items.getItemByCD(self.item.intCD)
            if vehicle.isInInventory:
                self.selectNoVehicle()
                self.onVehicleInventoryChanged()

    def isModified(self):
        if self.isPresent():
            for module in _MODULES_NAMES:
                currentModule = getattr(self.item.descriptor, module).compactDescr
                defaultModule = getattr(self.__defaultItem.descriptor, module).compactDescr
                if currentModule != defaultModule:
                    return True

        return False

    @process
    def installComponent(self, newId):
        newComponentItem = self.itemsCache.items.getItemByCD(newId)
        Waiting.show('applyModule', overlapsUI=False)
        conflictedEqs = newComponentItem.getConflictedEquipments(self.item)
        result = yield getPreviewInstallerProcessor(self.item, newComponentItem, conflictedEqs).request()
        from gui.shared.gui_items.items_actions.actions import processMsg
        processMsg(result)
        Waiting.hide('applyModule')
        if result.success:
            if self.__vehAppearance is not None:
                self.__vehAppearance.refreshVehicle(self.item)
            self.onComponentInstalled()
        return

    def hasModulesToSelect(self):
        return self.isPresent() and self.item.hasModulesToSelect

    def _addListeners(self):
        super(_CurrentPreviewVehicle, self)._addListeners()
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self._onUpdateUnlocks})

    def _selectVehicle(self, vehicleCD, vehicleStrCD=None):
        if self.isPresent() and self.item.intCD == vehicleCD:
            return
        else:
            Waiting.show('updateCurrentVehicle', isSingle=True, overlapsUI=False)
            self.onChangeStarted()
            self.__defaultItem = self.__getPreviewVehicle(vehicleCD)
            if vehicleStrCD is not None:
                self.__item = self.__makePreviewVehicleFromStrCD(vehicleStrCD)
            else:
                self.__item = self.__getPreviewVehicle(vehicleCD)
            if self.__vehAppearance is not None:
                self.__vehAppearance.refreshVehicle(self.__item)
            self._setChangeCallback()
            return

    def _onUpdateUnlocks(self, unlocks):
        if self.isPresent() and self.item.intCD in list(unlocks):
            self.item.isUnlocked = True
            self.onVehicleUnlocked()

    def __getPreviewVehicle(self, vehicleCD):
        if vehicleCD is not None:
            vehicle = self.itemsCache.items.getStockVehicle(vehicleCD, useInventory=True)
            if vehicle:
                vehicle.crew = vehicle.getPerfectCrew()
                return vehicle
        return

    def __makePreviewVehicleFromStrCD(self, vehicleStrCD):
        vehicle = Vehicle(strCompactDescr=vehicleStrCD, proxy=self.itemsCache.items)
        for slotID, device in enumerate(vehicle.optDevices):
            if device is not None:
                vehicle.descriptor.removeOptionalDevice(slotID)
                vehicle.optDevices[slotID] = None

        vehicle.crew = vehicle.getPerfectCrew()
        return vehicle


g_currentPreviewVehicle = _CurrentPreviewVehicle()
