# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_setups_ctrl.py
import logging
import typing
import BigWorld
from account_helpers.settings_core.settings_constants import GAME
from battle_modifiers_common import EXT_DATA_MODIFIERS_KEY
from constants import ARENA_PERIOD, VEHICLE_SIEGE_STATE
from gui.battle_control.arena_info.interfaces import IPrebattleSetupsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.items_parameters.functions import getVehicleFactors
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.MethodsRules import MethodsRules
from gui.veh_post_progression.helpers import setFeatures, setDisabledSwitches, getInstalledShells, updateInvInstalled
from gui.veh_post_progression.sounds import playSound, Sounds
from gui.veh_post_progression.battle_cooldown_manager import BattleCooldownManager
from helpers import dependency
from items import vehicles
from items.components.post_progression_components import getActiveModifications
from items.utils import getCircularVisionRadius, getFirstReloadTime
from PerksParametersController import PerksParametersController
from post_progression_common import EXT_DATA_PROGRESSION_KEY, EXT_DATA_SLOT_KEY, TANK_SETUP_GROUPS, TankSetupLayouts, TankSetups, VehicleState
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr
_logger = logging.getLogger(__name__)
_SWITCH_SETUPS_ACTION = 0
_EXT_ENHANCEMENTS_KEY = 'extEnhancements'
_EXT_PROGRESSION_MODS = 'extActiveProgression'
_EXT_RESPAWN_BOOST = 'respawnReloadTimeFactor'
_EXT_SIEGE_STATE_KEY = 'extSiegeState'
_SETUP_NAME_TO_LAYOUT = {TankSetups.SHELLS: TankSetupLayouts.SHELLS,
 TankSetups.EQUIPMENT: TankSetupLayouts.EQUIPMENT,
 TankSetups.OPTIONAL_DEVICES: TankSetupLayouts.OPTIONAL_DEVICES,
 TankSetups.BATTLE_BOOSTERS: TankSetupLayouts.BATTLE_BOOSTERS}

class _States(CONST_CONTAINER):
    IDLE = 0
    VEHICLE_ID = 1
    CREW = 2
    DYN_SLOT = 4
    ENHANCEMENTS = 8
    PERKS = 16
    PROGRESSION = 32
    RESPAWN = 64
    SETUPS = 128
    SETUPS_INDEXES = 256
    DISABLED_SWITCHES = 512
    INIT_COMPLETE = 1024
    SELECTION_STARTED = 2048
    SELECTION_STOPPED = 4096
    SELECTION_ENDED = 8192
    INIT_READY = VEHICLE_ID | CREW | DYN_SLOT | ENHANCEMENTS | PERKS | PROGRESSION | RESPAWN | SETUPS | SETUPS_INDEXES | DISABLED_SWITCHES
    SELECTION_AWAIT_HIDING = 16384


class IPrebattleSetupsListener(object):

    def showSetupsView(self, vehicle, isArenaLoaded=False):
        pass

    def updateVehicleParams(self, vehicle, factors, _):
        pass

    def updateVehicleSetups(self, vehicle):
        pass

    def stopSetupsSelection(self):
        pass

    def hideSetupsView(self):
        pass

    def onArenaLoaded(self):
        pass


class PrebattleSetupsController(MethodsRules, IPrebattleSetupsController):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__state', '__playerVehicleID', '__perksController', '__vehicle', '__invData', '__extData', '__hasValidCaps', '__cooldown', '__arenaLoaded')

    def __init__(self):
        super(PrebattleSetupsController, self).__init__()
        self.__state = _States.IDLE
        self.__invData = {}
        self.__extData = {}
        self.__playerVehicleID = None
        self.__perksController = None
        self.__vehicle = None
        self.__hasValidCaps = False
        self.__cooldown = BattleCooldownManager()
        self.__arenaLoaded = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL

    def getPrebattleSetupsVehicle(self):
        return self.__vehicle if self.isSelectionStarted() else None

    def getPrebattleVehicleID(self):
        return self.__playerVehicleID if self.isSelectionStarted() else 0

    def startControl(self, battleCtx, arenaVisitor):
        self.__hasValidCaps = arenaVisitor.bonus.hasSwitchSetups()
        self.__extData[_EXT_SIEGE_STATE_KEY] = VEHICLE_SIEGE_STATE.DISABLED
        self.__extData[EXT_DATA_MODIFIERS_KEY] = arenaVisitor.getArenaModifiers()

    def stopControl(self):
        self.clear(reset=True)
        self.__state = _States.IDLE
        self.__invData.clear()
        self.__extData.clear()
        self.__playerVehicleID = None
        self.__perksController = None
        self.__vehicle = None
        self.__hasValidCaps = False
        self.__arenaLoaded = False
        self.__cooldown.reset(_SWITCH_SETUPS_ACTION)
        return

    def isArenaLoaded(self):
        return self.__arenaLoaded

    def isSelectionStarted(self):
        return bool(self.__state & _States.SELECTION_STARTED)

    def isSelectionEnded(self):
        return bool(self.__state & (_States.SELECTION_ENDED | _States.SELECTION_STOPPED))

    @MethodsRules.delayable()
    def setPlayerVehicle(self, vehicleID, vehDescr):
        if self.__isSelectionStopped() or self.__state & _States.VEHICLE_ID:
            return
        self.__playerVehicleID = vehicleID
        self.__vehicle = Vehicle(strCompactDescr=vehDescr.makeCompactDescr())
        self.__onInitStepCompleted(_States.VEHICLE_ID)

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def stopSelection(self):
        if not self.__isSelectionStopped():
            self.__updateState(_States.SELECTION_STOPPED)
            self.__onFiniStepCompleted()

    @MethodsRules.delayable('setPlayerVehicle')
    def setCrew(self, vehicleID, crew):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.CREW:
            return
        self.__invData['battleCrewCDs'] = crew
        self.__onInitStepCompleted(_States.CREW)

    @MethodsRules.delayable('setPlayerVehicle')
    def setDynSlotType(self, vehicleID, dynSlotTypeID):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.DYN_SLOT:
            return
        self.__extData[EXT_DATA_SLOT_KEY] = dynSlotTypeID
        self.__onInitStepCompleted(_States.DYN_SLOT)

    @MethodsRules.delayable('setPlayerVehicle')
    def setEnhancements(self, vehicleID, enhancements):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.ENHANCEMENTS:
            return
        self.__extData[_EXT_ENHANCEMENTS_KEY] = enhancements
        self.__onInitStepCompleted(_States.ENHANCEMENTS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setPerks(self, vehicleID, perks):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.PERKS:
            return
        self.__perksController = PerksParametersController(self.__vehicle.compactDescr, perks)
        self.__onInitStepCompleted(_States.PERKS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setPostProgression(self, vehicleID, itemCDs):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.PROGRESSION:
            return
        self.__extData[_EXT_PROGRESSION_MODS] = getActiveModifications(itemCDs, vehicles.g_cache.postProgression())
        state = self.__extData.get(EXT_DATA_PROGRESSION_KEY, VehicleState())
        setFeatures(state, itemCDs)
        self.__extData[EXT_DATA_PROGRESSION_KEY] = state
        self.__onInitStepCompleted(_States.PROGRESSION)

    @MethodsRules.delayable('setPlayerVehicle')
    def setDisabledSwitches(self, vehicleID, groupIDs):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.DISABLED_SWITCHES:
            return
        state = self.__extData.get(EXT_DATA_PROGRESSION_KEY, VehicleState())
        setDisabledSwitches(state, groupIDs)
        self.__extData[EXT_DATA_PROGRESSION_KEY] = state
        self.__onInitStepCompleted(_States.DISABLED_SWITCHES)

    @MethodsRules.delayable('setPlayerVehicle')
    def setRespawnReloadFactor(self, vehicleID, reloadFactor):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.RESPAWN:
            return
        self.__extData[_EXT_RESPAWN_BOOST] = reloadFactor
        self.__onInitStepCompleted(_States.RESPAWN)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSetups(self, vehicleID, setups):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped() or self.__state & _States.SETUPS:
            return
        self.__invData.update({_SETUP_NAME_TO_LAYOUT[key]:value for key, value in setups.iteritems()})
        self.__onInitStepCompleted(_States.SETUPS)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSetupsIndexes(self, vehicleID, setupsIndexes):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped():
            return
        self.__invData['layoutIndexes'] = setupsIndexes
        updateInvInstalled(self.__invData, setupsIndexes)
        if self.__state & _States.SETUPS_INDEXES:
            self.__updateSetupIndexes()
            return
        self.__onInitStepCompleted(_States.SETUPS_INDEXES)

    @MethodsRules.delayable('setPlayerVehicle')
    def setSiegeState(self, vehicleID, siegeState):
        if self.__playerVehicleID != vehicleID or self.__isSelectionStopped():
            return
        self.__extData[_EXT_SIEGE_STATE_KEY] = siegeState
        if self.__state & _States.SELECTION_STARTED:
            self.__updateSiegeState()

    @MethodsRules.delayable('setPlayerVehicle')
    def setVehicleAttrs(self, vehicleID, attrs):
        if not self.isSelectionStarted() or self.__playerVehicleID != vehicleID:
            return
        newFactors = getVehicleFactors(self.__vehicle)
        newFactors[_EXT_RESPAWN_BOOST] = self.__extData[_EXT_RESPAWN_BOOST]
        newAttrs = dict(attrs)
        newAttrs['circularVisionRadius'] = getCircularVisionRadius(self.__vehicle.descriptor, newFactors)
        self.__sessionProvider.shared.feedback.setVehicleAttrs(self.__playerVehicleID, newAttrs)

    def setViewComponents(self, *components):
        if self.__isSelectionStopped():
            return
        self._viewComponents = components
        if self.isSelectionStarted():
            for component in components:
                component.showSetupsView(self.__vehicle, self.__arenaLoaded)

    def arenaLoadCompleted(self):
        self.__arenaLoaded = True
        if not self.__settingsCore.getSetting(GAME.SWITCH_SETUPS_IN_LOADING):
            self.__onStartSelection()
        else:
            for component in self._viewComponents:
                component.onArenaLoaded()

            self.__onFiniStepCompleted()

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        if not self.__isSelectionStopped():
            self.__updatePeriod(period)

    def switchLayout(self, groupID, layoutIdx):
        if self.__sessionProvider.isReplayPlaying:
            return
        elif not self.isSelectionStarted():
            return
        elif self.__cooldown.isInProcess(_SWITCH_SETUPS_ACTION):
            return
        elif not self.__vehicle.isSetupSwitchActive(groupID):
            return
        elif self.__vehicle.postProgression.isPrebattleSwitchDisabled(groupID):
            return
        else:
            playerVehicle = BigWorld.entities.get(self.__playerVehicleID)
            if playerVehicle is None:
                return
            self.__cooldown.process(_SWITCH_SETUPS_ACTION)
            playerVehicle.cell.switchSetup(groupID, layoutIdx)
            playSound(Sounds.GAMEPLAY_SETUP_SWITCH)
            return

    def __isSelectionAvailable(self):
        if not self.__hasValidCaps:
            return False
        for groupID in TANK_SETUP_GROUPS.iterkeys():
            if self.__vehicle.isSetupSwitchActive(groupID) and not self.__vehicle.postProgression.isPrebattleSwitchDisabled(groupID):
                return True

        return False

    def __isSelectionStopped(self):
        return bool(self.__state & _States.SELECTION_STOPPED)

    def __isSelectionShouldEnded(self):
        return self.__arenaLoaded and self.__isSelectionStopped() if self.__settingsCore.getSetting(GAME.SWITCH_SETUPS_IN_LOADING) else self.__isSelectionStopped()

    def __isSelectionShouldStarted(self):
        return self.__state & _States.INIT_COMPLETE and self.__isSelectionAvailable() if self.__settingsCore.getSetting(GAME.SWITCH_SETUPS_IN_LOADING) else self.__state & _States.INIT_COMPLETE and self.__isSelectionAvailable() and self.isArenaLoaded()

    def __onInitStepCompleted(self, stepState):
        if self.__state & _States.INIT_COMPLETE:
            return
        self.__updateState(stepState)
        if self.__state & _States.INIT_READY == _States.INIT_READY:
            shellsCDs = [ shell.intCD for shell in self.__vehicle.gun.defaultAmmo ]
            shellsLayoutKey = (self.__vehicle.turret.intCD, self.__vehicle.gun.intCD)
            self.__invData['shells'] = getInstalledShells(shellsCDs, self.__invData[TankSetupLayouts.SHELLS])
            self.__invData[TankSetupLayouts.SHELLS] = {shellsLayoutKey: self.__invData[TankSetupLayouts.SHELLS]}
            self.__updateGuiVehicle()
            self.__updateState(_States.INIT_COMPLETE)
        self.__onStartSelection()

    def __onFiniStepCompleted(self):
        if self.__state & _States.SELECTION_ENDED:
            return
        if self.__isSelectionShouldEnded():
            self.__updateState(_States.SELECTION_ENDED)

    def __onStartSelection(self):
        if self.__state & _States.SELECTION_STARTED or self.__isSelectionStopped():
            return
        if self.__isSelectionShouldStarted():
            self.__updateState(_States.SELECTION_STARTED)

    def __updateAmmoCtrl(self):
        self.__sessionProvider.shared.ammo.updateForNewSetup(self.__vehicle.descriptor.gun, self.__vehicle.shells.installed.getItems())

    def __updateAmmoCtrlParams(self, factors):
        ammoCtrl = self.__sessionProvider.shared.ammo
        hasAmmo = any((shell.count for shell in self.__vehicle.shells.installed.getItems()))
        reloadTime = getFirstReloadTime(self.__vehicle.descriptor, factors) if hasAmmo else 0.0
        ammoCtrl.setGunReloadTime(-1, reloadTime, skipAutoLoader=True)

    def __updateFeedbackParams(self, factors):
        feedbackCtrl = self.__sessionProvider.shared.feedback
        newAttrs = feedbackCtrl.getVehicleAttrs()
        newAttrs['circularVisionRadius'] = getCircularVisionRadius(self.__vehicle.descriptor, factors)
        feedbackCtrl.setVehicleAttrs(self.__playerVehicleID, newAttrs)

    def __updateGuiVehicle(self):
        invData, extData = self.__invData.copy(), self.__extData.copy()
        vehicle = self.__vehicle = Vehicle(strCompactDescr=self.__vehicle.strCD, extData=extData, invData=invData)
        vehicle.installPostProgressionItem(self.__itemsFactory.createVehPostProgression(vehicle.compactDescr, self.__extData[EXT_DATA_PROGRESSION_KEY], vehicle.typeDescr))
        vehicle.setPerksController(self.__perksController)
        vehicle.descriptor.onSiegeStateChanged(self.__extData[_EXT_SIEGE_STATE_KEY])
        vehicle.descriptor.installModifications(self.__extData[_EXT_PROGRESSION_MODS], rebuildAttrs=False)
        vehicle.descriptor.installEnhancements(self.__extData[_EXT_ENHANCEMENTS_KEY], rebuildAttrs=False)
        vehicle.descriptor.installOptDevsSequence(vehicle.optDevices.installed.getIntCDs())
        newFactors = getVehicleFactors(vehicle)
        newFactors[_EXT_RESPAWN_BOOST] = self.__extData[_EXT_RESPAWN_BOOST]
        return newFactors

    def __updatePeriod(self, period):
        if period >= ARENA_PERIOD.BATTLE:
            self.stopSelection()

    def __updateState(self, addMask):
        if addMask == _States.SELECTION_STARTED:
            for component in self._viewComponents:
                component.showSetupsView(self.__vehicle, self.__arenaLoaded)

            self.__updateAmmoCtrl()
        if addMask == _States.SELECTION_STOPPED and self.isSelectionStarted():
            self.__state |= _States.SELECTION_AWAIT_HIDING
            self.__state &= ~_States.SELECTION_STARTED
            self.__vehicle.stopPerksController()
            for component in self._viewComponents:
                component.stopSetupsSelection()

        if addMask == _States.SELECTION_ENDED and self.__state & _States.SELECTION_AWAIT_HIDING:
            self.__state &= ~_States.SELECTION_AWAIT_HIDING
            for component in self._viewComponents:
                component.hideSetupsView()

        self.__state |= addMask
        _logger.debug('[PrebattleSetupsController] addMask %s modifiedState %s', addMask, self.__state)

    def __updateSetupIndexes(self):
        newFactors = self.__updateGuiVehicle()
        self.__updateAmmoCtrl()
        self.__updateAmmoCtrlParams(newFactors)
        self.__updateFeedbackParams(newFactors)
        for component in self._viewComponents:
            component.updateVehicleParams(self.__vehicle, newFactors, self.__playerVehicleID)
            component.updateVehicleSetups(self.__vehicle)

        if self.__sessionProvider.isReplayPlaying:
            playSound(Sounds.GAMEPLAY_SETUP_SWITCH)

    def __updateSiegeState(self):
        newFactors = self.__updateGuiVehicle()
        self.__updateAmmoCtrlParams(newFactors)
        self.__updateFeedbackParams(newFactors)
        for component in self._viewComponents:
            component.updateVehicleParams(self.__vehicle, newFactors, self.__playerVehicleID)
