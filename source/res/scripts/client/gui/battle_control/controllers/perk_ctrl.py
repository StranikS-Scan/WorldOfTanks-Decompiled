# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/perk_ctrl.py
from typing import TYPE_CHECKING
from copy import deepcopy
import BigWorld
import Event
from helpers import dependency
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from skeletons.gui.battle_session import IBattleSessionProvider
if TYPE_CHECKING:
    from Vehicle import Vehicle
_UPDATE_FUN_PREFIX = '_updatePerk'
_DATA_KEY_PERK_ID = 'perkID'

class PerksController(ViewComponentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PerksController, self).__init__()
        self.onPerkChanged = Event.Event()
        self._prevPanelState = {}
        self._prevRibbonsState = {}
        self._prevArenaPeriod = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERKS

    def updatePerks(self, perks):
        changes, currentPanelState = self._getCurrentState(perks, self._prevPanelState)
        if self._isInBattle():
            for viewCmp in self._viewComponents:
                viewCmp.updatePerks(changes, self._prevPanelState)

        for perkID, data in changes.iteritems():
            updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
            if updater is not None:
                updater(perkID=perkID, **data)

        self._prevPanelState = deepcopy(currentPanelState)
        return

    def notifyRibbonChanges(self, ribbons):
        if not self._isInBattle():
            return
        changes, currentRibbonsState = self._getCurrentState(ribbons, self._prevRibbonsState)
        for perkID, perkData in sorted(changes.iteritems(), key=lambda item: item[1]['endTime']):
            if perkData['endTime'] > BigWorld.serverTime():
                self.onPerkChanged({_DATA_KEY_PERK_ID: perkID})

        self._prevRibbonsState = deepcopy(currentRibbonsState)

    def startControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self._onVehicleControlling
        g_playerEvents.onArenaPeriodChange += self._onArenaPeriodChange
        return

    def stopControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self._onVehicleControlling
        self.onPerkChanged.clear()
        g_playerEvents.onArenaPeriodChange -= self._onArenaPeriodChange
        return

    def _onVehicleControlling(self, vehicle):
        for perkID, data in self._prevPanelState.iteritems():
            updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
            if updater is not None:
                updater(vehicle=vehicle, perkID=perkID, **data)

        if self._isInBattle():
            for viewCmp in self._viewComponents:
                viewCmp.setPerks(vehicle.perks)

        return

    def _isInBattle(self):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        return periodCtrl is not None and periodCtrl.getPeriod() == ARENA_PERIOD.BATTLE

    def _onArenaPeriodChange(self, period, *args):
        if self._prevArenaPeriod == period:
            return
        self._prevArenaPeriod = period
        if period != ARENA_PERIOD.BATTLE:
            return
        ctrl = self.sessionProvider.shared.vehicleState
        vehicle = ctrl.getControllingVehicle()
        if not vehicle:
            return
        for viewCmp in self._viewComponents:
            viewCmp.setPerks(vehicle.perks)
            viewCmp.updatePerks(self._prevPanelState, {})

        for perkID in self._prevPanelState.keys():
            self.onPerkChanged({_DATA_KEY_PERK_ID: perkID})

    @staticmethod
    def _getCurrentState(source, prevState):
        currentState = {item[_DATA_KEY_PERK_ID]:{key:item[key] for key in set(item.keys()) ^ {_DATA_KEY_PERK_ID}} for item in source}
        changes = {perkID:data for perkID, data in currentState.iteritems() if perkID not in prevState or prevState[perkID] != data}
        return (changes, currentState)

    def _updatePerk403(self, perkID, state, coolDown, lifeTime, vehicle=None):
        isActive = bool(state)
        if vehicle is None:
            vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            BigWorld.player().updateVehicleQuickShellChanger(vehicle.id, isActive)
        return
