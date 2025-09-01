# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/pillbox_siege_widget.py
from collections import namedtuple
import BigWorld
import typing
import CommandMapping
from PillboxSiegeComponent import PillboxSiegeComponent
from constants import VEHICLE_SIEGE_STATE as PILLBOX_STATES, VEHICLE_MISC_STATUS
from events_handler import eventHandler
from helpers import dependency
from gui.battle_control.battle_constants import DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED, VEHICLE_DEVICE_IN_COMPLEX_ITEM
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.PillboxSiegeWidgetMeta import PillboxSiegeWidgetMeta
from gui.Scaleform.genConsts.PILLBOX_SIEGE_WIDGET_CONST import PILLBOX_SIEGE_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanic_commands_view_updater import MechanicsCommandsUpdater
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.vehicle_device_view_updater import IVehicleDeviceStatusView, VehicleDeviceStatusUpdater
from gui.veh_mechanics.battle.updaters.vehicle_misc_status_view_updater import VehicleMiscStatusUpdater, IVehicleMiscStatusView, MISC_STATUS_LEVEL_CRITICAL, MISC_STATUS_LEVEL_WARNING
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_commands import IMechanicCommandsListenerLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events import ComponentListener
if typing.TYPE_CHECKING:
    from PillboxSiegeComponent import PillboxSiegeModeState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from gui.veh_mechanics.battle.updaters.vehicle_misc_status_view_updater import _ObservableMiscStatuses
_HotKeyInfo = namedtuple('_HotKeyInfo', ['affectOn', 'duration'])

class PillboxSiegeMechanicWidget(PillboxSiegeWidgetMeta, ComponentListener, IMechanicStatesListenerLogic, IMechanicCommandsListenerLogic, IVehicleMiscStatusView, IVehicleDeviceStatusView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _PILLBOX_SIEGE_UI_STATES = {(PILLBOX_STATES.DISABLED, PILLBOX_STATES.DISABLED): PILLBOX_SIEGE_WIDGET_CONST.IDLE,
     (PILLBOX_STATES.ENABLED, PILLBOX_STATES.ENABLED): PILLBOX_SIEGE_WIDGET_CONST.SIEDGE,
     (PILLBOX_STATES.PILLBOX_ENABLED, PILLBOX_STATES.PILLBOX_ENABLED): PILLBOX_SIEGE_WIDGET_CONST.PILLBOX,
     (PILLBOX_STATES.DISABLED, PILLBOX_STATES.ENABLED): PILLBOX_SIEGE_WIDGET_CONST.IDLE_TO_SIEDGE,
     (PILLBOX_STATES.DISABLED, PILLBOX_STATES.PILLBOX_ENABLED): PILLBOX_SIEGE_WIDGET_CONST.IDLE_TO_PILLBOX,
     (PILLBOX_STATES.ENABLED, PILLBOX_STATES.DISABLED): PILLBOX_SIEGE_WIDGET_CONST.SIEDGE_TO_IDLE,
     (PILLBOX_STATES.ENABLED, PILLBOX_STATES.PILLBOX_ENABLED): PILLBOX_SIEGE_WIDGET_CONST.SIEDGE_TO_PILLBOX,
     (PILLBOX_STATES.PILLBOX_ENABLED, PILLBOX_STATES.DISABLED): PILLBOX_SIEGE_WIDGET_CONST.PILLBOX_TO_IDLE,
     (PILLBOX_STATES.PILLBOX_ENABLED, PILLBOX_STATES.ENABLED): PILLBOX_SIEGE_WIDGET_CONST.PILLBOX_TO_SIEDGE}
    _PILLBOX_CONDITIONS = {DEVICE_STATE_CRITICAL: PILLBOX_SIEGE_WIDGET_CONST.CONDITION_WARNING,
     DEVICE_STATE_DESTROYED: PILLBOX_SIEGE_WIDGET_CONST.CONDITION_CRITICAL}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, True), HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}
    _HOT_KEY_UI_MAP = {VehicleMechanicCommand.ACTIVATE: _HotKeyInfo(VehicleMechanicCommand.ACTIVATE.value, 0),
     VehicleMechanicCommand.ALTERNATIVE_ACTIVATE: _HotKeyInfo(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, 0),
     VehicleMechanicCommand.PREPARING: _HotKeyInfo(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, PillboxSiegeComponent.DURATION),
     VehicleMechanicCommand.CANCELLED: _HotKeyInfo(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, 0)}
    _VEHICLE_MISC_OBSERVE = {VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED: (MISC_STATUS_LEVEL_CRITICAL, MISC_STATUS_LEVEL_WARNING),
     VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING: (MISC_STATUS_LEVEL_CRITICAL,)}
    _VEHICLE_DEVICES_OBSERVE = {'leftTrack0': (DEVICE_STATE_DESTROYED,),
     'rightTrack0': (DEVICE_STATE_DESTROYED,),
     'engine': (DEVICE_STATE_CRITICAL, DEVICE_STATE_DESTROYED)}

    def __init__(self):
        super(PillboxSiegeMechanicWidget, self).__init__()
        self.__miscStatuses = None
        self.__devicesStatuses = {}
        return

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateTick(self, state):
        if state.isStateSwitching:
            self.__invalidateProgress(state)

    @eventHandler
    def onMechanicCommand(self, command):
        if command in self._HOT_KEY_UI_MAP:
            keyInfo = self._HOT_KEY_UI_MAP[command]
            self.as_setCommandS(command.value, keyInfo.affectOn, keyInfo.duration)

    def vehicleMiscStatusChanged(self, miscStatuses):
        self.__miscStatuses = miscStatuses
        self.__invalidateCondition()

    def vehicleDeviceStatusChanged(self, devicesStatuses):
        self.__devicesStatuses = devicesStatuses
        self.as_setDeviceStatesS([ self.__makeDeviceState(*deviceStatus) for deviceStatus in devicesStatuses.items() ])
        self.__invalidateCondition()

    def _dispose(self):
        self.__miscStatuses = None
        super(PillboxSiegeMechanicWidget, self)._dispose()
        return

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.PILLBOX_SIEGE_MODE, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.PILLBOX_SIEGE_MODE, self),
         VehicleMiscStatusUpdater(self._VEHICLE_MISC_OBSERVE, self),
         VehicleDeviceStatusUpdater(self._VEHICLE_DEVICES_OBSERVE, self),
         MechanicsCommandsUpdater(VehicleMechanic.PILLBOX_SIEGE_MODE, self),
         HotKeysViewUpdater(self._HOT_KEY_MAP.keys(), self)]

    def __getDisplayState(self, state):
        key = (state.state, state.nextState)
        return self._PILLBOX_SIEGE_UI_STATES[key] if key in self._PILLBOX_SIEGE_UI_STATES else PILLBOX_SIEGE_WIDGET_CONST.IDLE

    def __getCondition(self):
        player = BigWorld.player()
        vehicle = self.__sessionProvider.shared.vehicleState.getControllingVehicle()
        if player is None or vehicle is None:
            return PILLBOX_SIEGE_WIDGET_CONST.CONDITION_NORMAL
        else:
            return PILLBOX_SIEGE_WIDGET_CONST.CONDITION_CRITICAL if self.__miscStatuses and self.__miscStatuses.hasNegativeEffect else self._PILLBOX_CONDITIONS.get(self.__devicesStatuses.get('engine'), PILLBOX_SIEGE_WIDGET_CONST.CONDITION_NORMAL)

    def __makeDeviceState(self, deviceName, deviceState):
        return {'deviceName': VEHICLE_DEVICE_IN_COMPLEX_ITEM.get(deviceName, deviceName),
         'deviceState': deviceState}

    def __invalidateState(self, state, isInstantly=False):
        self.__invalidateProgress(state)
        self.as_setStateS(self.__getDisplayState(state), isInstantly)

    def __invalidateProgress(self, state):
        self.as_setProgressS(state.progress, state.timeLeft)

    def __invalidateCondition(self):
        self.as_setConditionS(self.__getCondition(), self.__devicesStatuses.get('engine') != DEVICE_STATE_DESTROYED)
