# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/entity.py
from debug_utils import LOG_ERROR
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.permissions import SquadPermissions
from gui.prb_control.entities.base.unit.entity import UnitEntryPoint, UnitEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import g_itemsCache
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA

class SquadEntryPoint(UnitEntryPoint):
    """
    Squad base entry point
    """

    def makeDefCtx(self):
        return SquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def join(self, ctx, callback=None):
        super(SquadEntryPoint, self).join(ctx, callback)
        LOG_ERROR('Player can join to squad by invite only')
        if callback:
            callback(False)


class SquadEntity(UnitEntity):
    """
    Squad base entity class
    """

    def init(self, ctx=None):
        self.invalidateVehicleStates()
        return super(SquadEntity, self).init(ctx)

    def canKeepMode(self):
        return False

    def hasLockedState(self):
        pInfo = self.getPlayerInfo()
        return pInfo.isReady and super(SquadEntity, self).hasLockedState()

    def unit_onUnitRosterChanged(self):
        rosterSettings = self._createRosterSettings()
        if rosterSettings != self._rosterSettings:
            self._rosterSettings = rosterSettings
            self.invalidateVehicleStates()
            self._vehiclesWatcher.validate()
        self._invokeListeners('onUnitRosterChanged')
        g_eventDispatcher.updateUI()

    def rejoin(self):
        super(SquadEntity, self).rejoin()
        self.unit_onUnitRosterChanged()

    def invalidateVehicleStates(self, vehicles=None):
        """
        Invalidates given vehicles states
        Args:
            vehicles: dict of items cache request result: intCD -> vehicle item
        """
        state = Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT
        if vehicles:
            criteria = REQ_CRITERIA.IN_CD_LIST(vehicles)
        else:
            criteria = REQ_CRITERIA.INVENTORY
        vehicles = g_itemsCache.items.getVehicles(criteria)
        updatedVehicles = [ intCD for intCD, v in vehicles.iteritems() if self._updateVehicleState(v, state) ]
        if updatedVehicles:
            g_prbCtrlEvents.onVehicleClientStateChanged(updatedVehicles)

    def _buildPermissions(self, roles, flags, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        return SquadPermissions(roles, flags, isCurrentPlayer, isPlayerReady)

    def _createActionsHandler(self):
        return SquadActionsHandler(self)

    def _createActionsValidator(self):
        return SquadActionsValidator(self)

    def _vehicleStateCondition(self, v):
        """
        Checker for vehicle state
        Args:
            v: vehicle item
        """
        return True

    def _updateVehicleState(self, vehicle, state):
        """
        Updates vehicle custom state set by this entity
        Args:
            vehicle: vehicle item
            state: new state
        
        Returns:
            state set
        """
        invalid = not self._vehicleStateCondition(vehicle)
        stateSet = vehicle.getCustomState() == state
        changed = invalid ^ stateSet
        if changed:
            if invalid:
                vehicle.setCustomState(state)
            else:
                vehicle.clearCustomState()
        return changed
