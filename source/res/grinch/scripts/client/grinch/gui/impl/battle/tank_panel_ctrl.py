# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/tank_panel_ctrl.py
import typing
import BigWorld
from grinch_common.grinch_constants import GrinchAbilities
from constants import EQUIPMENT_STAGES
from helpers import dependency
from helpers.events_handler import EventsHandler
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from grinch.gui.shared.events import RageAbilityEvent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from VehicleRespawnComponent import VehicleRespawnComponent
if typing.TYPE_CHECKING:
    from grinch.gui.impl.gen.view_models.views.battle.grinch_hud.tank_panel_model import TankPanelModel
    from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem
    from Vehicle import Vehicle
_LEFT_TRACK_DEVICE_NAME = 'leftTrack0'
_RIGHT_TRACK_DEVICE_NAME = 'rightTrack0'
_WATCHED_STATES = (VEHICLE_VIEW_STATE.HEALTH, VEHICLE_VIEW_STATE.SPEED, VEHICLE_VIEW_STATE.DEVICES)

class TankPanelCtrl(EventsHandler):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hudRef):
        super(TankPanelCtrl, self).__init__()
        self.__hudRef = hudRef
        self.__maxHealth = 0
        eqCtrl = self._sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            for stateID in _WATCHED_STATES:
                value = ctrl.getStateValue(stateID)
                if value is None:
                    continue
                if stateID == VEHICLE_VIEW_STATE.DEVICES:
                    for v in value:
                        self.__onVehicleStateUpdated(stateID, v)

                self.__onVehicleStateUpdated(stateID, value)

        VehicleRespawnComponent.onVehicleRespawned += self.__vehicleRespawnHandler
        self.__updateMaxHealth()
        self._subscribe()
        return

    def _getListeners(self):
        listeners = [(RageAbilityEvent.VEHICLE_STATUS_CHANGED,
          self.__onRageVehicleStatusUpdate,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]
        return listeners

    @property
    def viewModel(self):
        return self.__hudRef.viewModel.tankPanel

    def dispose(self):
        self.__hudRef = None
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        eqCtrl = self._sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        VehicleRespawnComponent.onVehicleRespawned -= self.__vehicleRespawnHandler
        self._unsubscribe()
        return

    def updateVehicleParams(self, vehicle, _):
        self.__updateMaxHealth()
        self._updateHealth(self.__maxHealth)

    def _updateSpeed(self, speed):
        with self.viewModel.transaction() as model:
            model.setSpeed(speed)

    def _updateHealthFromServer(self, health):
        if self._sessionProvider.shared.prebattleSetups.isSelectionStarted():
            return
        self.__updateMaxHealth()
        self._updateHealth(health)

    def _updateHealth(self, health):
        if health <= self.__maxHealth and self.__maxHealth > 0:
            with self.viewModel.transaction() as model:
                model.setHealth(health)
                model.setMaxHealth(self.__maxHealth)

    def _updateDeviceState(self, value):
        device, state = value[:2]
        isDestroyed = bool(state == 'destroyed')
        if device == _LEFT_TRACK_DEVICE_NAME:
            with self.viewModel.transaction() as model:
                model.setLeftTrackDestroyed(isDestroyed)
        if device == _RIGHT_TRACK_DEVICE_NAME:
            with self.viewModel.transaction() as model:
                model.setRightTrackDestroyed(isDestroyed)

    def __updateMaxHealth(self):
        vehStateCtrl = self._sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehicle = vehStateCtrl.getControllingVehicle()
            self.__maxHealth = vehicle.maxHealth
        return

    def __onVehicleStateUpdated(self, state, value):
        if state not in _WATCHED_STATES:
            return
        if state == VEHICLE_VIEW_STATE.SPEED:
            self._updateSpeed(value)
        if state == VEHICLE_VIEW_STATE.DEVICES:
            self._updateDeviceState(value)
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self._updateHealthFromServer(value)

    def __onEquipmentUpdated(self, intCD, item):
        if item.getDescriptor().name != GrinchAbilities.GRINCH_RAGE:
            return
        stage = item.getStage()
        prevStage = item.getPrevStage()
        if EQUIPMENT_STAGES.ACTIVE not in (stage, prevStage):
            return
        with self.viewModel.transaction() as model:
            model.setRageMode(stage == EQUIPMENT_STAGES.ACTIVE)

    def __onRageVehicleStatusUpdate(self, event):
        playerVehicleID = BigWorld.player().playerVehicleID
        if playerVehicleID == event.vehicleID:
            with self.viewModel.transaction() as model:
                model.setIsUndead(event.vehicleUndeadStatus)

    def __vehicleRespawnHandler(self, vehicle):
        if not vehicle.isPlayerVehicle:
            return
        with self.viewModel.transaction() as model:
            model.setLeftTrackDestroyed(False)
        with self.viewModel.transaction() as model:
            model.setRightTrackDestroyed(False)
