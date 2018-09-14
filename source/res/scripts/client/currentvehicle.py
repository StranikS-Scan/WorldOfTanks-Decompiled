# Embedded file name: scripts/client/CurrentVehicle.py
import random
import BigWorld
from Event import Event
from gui.Scaleform.framework.managers.TextManager import TextManager, TextIcons
from gui.shared.formatters.time_formatters import getRentLeftTimeStr
from items import vehicles
from helpers import isPlayerAccount, i18n
from account_helpers.AccountSettings import AccountSettings, CURRENT_VEHICLE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui import prb_control, game_control, g_tankActiveCamouflage
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.Waiting import Waiting

class _CurrentVehicle():

    def __init__(self):
        self.__vehInvID = 0
        self.__changeCallbackID = None
        self.__historicalBattle = None
        self.onChanged = Event()
        self.onChangeStarted = Event()
        return

    def init(self):
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate,
         'cache.vehsLock': self.onLocksUpdate})
        game_control.g_instance.igr.onIgrTypeChanged += self.onIgrTypeChanged
        game_control.g_instance.rentals.onRentChangeNotify += self.onRentChange
        prbVehicle = self.__checkPrebattleLockedVehicle()
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        self.selectVehicle(prbVehicle or storedVehInvID)

    def destroy(self):
        self.__vehInvID = 0
        self.__clearChangeCallback()
        self.onChanged.clear()
        self.onChangeStarted.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        game_control.g_instance.igr.onIgrTypeChanged -= self.onIgrTypeChanged
        game_control.g_instance.rentals.onRentChangeNotify -= self.onRentChange
        g_hangarSpace.removeVehicle()
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
            isCustomizationChanged = 'igrCustomizationLayout' in vehsDiff and self.__vehInvID in vehsDiff['igrCustomizationLayout']
            isComponentsChanged = GUI_ITEM_TYPE.TURRET in invDiff or GUI_ITEM_TYPE.GUN in invDiff
            isVehicleChanged = len(filter(lambda hive: self.__vehInvID in hive or (self.__vehInvID, '_r') in hive, vehsDiff.itervalues())) > 0
            if isComponentsChanged or isRepaired or isVehicleDescrChanged or isCustomizationChanged:
                self.refreshModel()
            if isVehicleChanged or isRepaired:
                self.onChanged()
        return

    def onLocksUpdate(self, locksDiff):
        if self.__vehInvID in locksDiff:
            self.refreshModel()

    def refreshModel(self):
        if self.isPresent() and self.isInHangar() and self.item.modelState:
            if self.__historicalBattle is not None:
                historical = g_tankActiveCamouflage['historical']
                if self.__historicalBattle.canParticipateWith(self.item.intCD) and self.item.intCD not in historical:
                    historical[self.item.intCD] = self.__historicalBattle.getArenaType().vehicleCamouflageKind
            if self.item.intCD not in g_tankActiveCamouflage:
                availableKinds = []
                currKind = 0
                for id, startTime, days in self.item.descriptor.camouflages:
                    if id is not None:
                        availableKinds.append(currKind)
                    currKind += 1

                if len(availableKinds) > 0:
                    g_tankActiveCamouflage[self.item.intCD] = random.choice(availableKinds)
            g_hangarSpace.updateVehicle(self.item, self.__historicalBattle)
        else:
            g_hangarSpace.removeVehicle()
        return

    @property
    def invID(self):
        return self.__vehInvID

    @property
    def item(self):
        if self.__vehInvID > 0:
            return g_itemsCache.items.getVehicle(self.__vehInvID)
        else:
            return None

    def isPresent(self):
        return self.item is not None

    def isBroken(self):
        return self.isPresent() and self.item.isBroken

    def isGroupReady(self):
        if self.isPresent():
            if self.item.isOnlyForEventBattles:
                return not self.item.isGroupBroken() and self.item.isGroupCrewFull() and self.item.isGroupAmmoFull() and self.item.isAmmoFull
            return True
        else:
            return False

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

    def isAlive(self):
        return self.isPresent() and self.item.isAlive

    def isReadyToPrebattle(self):
        return self.isPresent() and self.item.isReadyToPrebattle()

    def isReadyToFight(self):
        return self.isPresent() and self.item.isReadyToFight

    def isAutoLoadFull(self):
        if self.isPresent() and self.item.isAutoLoad:
            for shell in self.item.shells:
                if shell.count != shell.defaultCount:
                    return False

        return True

    def isAutoEquipFull(self):
        if self.isPresent() and self.item.isAutoEquip:
            for i, e in enumerate(self.item.eqsLayout):
                if e != self.item.eqs[i]:
                    return False

        return True

    def selectVehicle(self, vehInvID = 0):
        vehicle = g_itemsCache.items.getVehicle(vehInvID)
        if vehicle is None:
            invVehs = g_itemsCache.items.getVehicles(criteria=REQ_CRITERIA.INVENTORY)
            if len(invVehs):
                vehInvID = sorted(invVehs.itervalues())[0].invID
            else:
                vehInvID = 0
        self.__selectVehicle(vehInvID)
        return

    def selectNoVehicle(self):
        self.__selectVehicle(0)

    def getHangarMessage(self):
        if self.isPresent():
            state, stateLvl = self.item.getState()
            if state == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
                localization = '#menu:vehicle/igrRentLeft/%s'
                rentLeftStr = getRentLeftTimeStr(localization, self.item.rentLeftTime)
                icon = TextManager.getIcon(TextIcons.PREMIUM_IGR_BIG)
                if self.item.isRented:
                    message = i18n.makeString('#menu:currentVehicleStatus/' + state, icon=icon, time=rentLeftStr)
                else:
                    message = i18n.makeString('#menu:tankCarousel/vehicleStates/inPremiumIgrOnly', icon=icon)
                return (state, message, stateLvl)
            return (state, '#menu:currentVehicleStatus/' + state, stateLvl)
        return ('notpresent', MENU.CURRENTVEHICLESTATUS_NOTPRESENT, Vehicle.VEHICLE_STATE_LEVEL.CRITICAL)

    def setHistoricalBattle(self, historicalBattle):
        g_tankActiveCamouflage['historical'] = {}
        self.__historicalBattle = historicalBattle
        self.refreshModel()
        self.onChanged()

    def __selectVehicle(self, vehInvID):
        if vehInvID == self.__vehInvID:
            return
        Waiting.show('updateCurrentVehicle', isSingle=True)
        self.onChangeStarted()
        self.__vehInvID = vehInvID
        AccountSettings.setFavorites(CURRENT_VEHICLE, vehInvID)
        self.refreshModel()
        if not self.__changeCallbackID:
            self.__changeCallbackID = BigWorld.callback(0.1, self.__changeDone)

    def __changeDone(self):
        self.__clearChangeCallback()
        if isPlayerAccount():
            self.onChanged()
        Waiting.hide('updateCurrentVehicle')

    def __clearChangeCallback(self):
        if self.__changeCallbackID is not None:
            BigWorld.cancelCallback(self.__changeCallbackID)
            self.__changeCallbackID = None
        return

    def __checkPrebattleLockedVehicle(self):
        clientPrb = prb_control.getClientPrebattle()
        if clientPrb is not None:
            rosters = prb_control.getPrebattleRosters(prebattle=clientPrb)
            for rId, roster in rosters.iteritems():
                if BigWorld.player().id in roster:
                    vehCompDescr = roster[BigWorld.player().id].get('vehCompDescr', '')
                    if len(vehCompDescr):
                        vehDescr = vehicles.VehicleDescr(vehCompDescr)
                        vehicle = g_itemsCache.items.getItemByCD(vehDescr.type.compactDescr)
                        if vehicle is not None:
                            return vehicle.invID

        return 0

    def __repr__(self):
        return 'CurrentVehicle(%s)' % str(self.item)


g_currentVehicle = _CurrentVehicle()
