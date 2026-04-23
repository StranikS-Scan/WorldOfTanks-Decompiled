# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/propellant_gun_widget.py
from __future__ import absolute_import, division
import typing
import CommandMapping
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.PropellantGunWidgetMeta import PropellantGunWidgetMeta
from gui.Scaleform.genConsts.PROPELLANT_GUN_WIDGET_CONST import PROPELLANT_GUN_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.crosshair_type_updater import CrosshairTypeUpdater
from gui.veh_mechanics.battle.updaters.current_shell_damage_updater import CurrentShellDamageUpdater
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_commands_updater import VehicleMechanicCommandsUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_life_cycle_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.gun_mechanics.propellant_gun import DEFAULT_PROPELLANT_GUN_MECHANIC_STATE
from vehicles.mechanics.mechanic_commands import IMechanicCommandsListenerLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.gun_mechanics.propellant_gun import IPropellantGunMechanicState, IPropellantGunComponentParams

class PropellantGunMechanicWidget(PropellantGunWidgetMeta, ContainersListener, IComponentLifeCycleListenerLogic, IMechanicStatesListenerLogic, IMechanicCommandsListenerLogic):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}
    _GUI_STATE_MAP = {(True, True): PROPELLANT_GUN_WIDGET_CONST.ACTIVE_ENABLED,
     (False, True): PROPELLANT_GUN_WIDGET_CONST.READY_ENABLED,
     (True, False): PROPELLANT_GUN_WIDGET_CONST.ACTIVE_DISABLED,
     (False, False): PROPELLANT_GUN_WIDGET_CONST.READY_DISABLED}

    def __init__(self):
        super(PropellantGunMechanicWidget, self).__init__()
        self.__overchargeThreshold = 1.0
        self.__shellDamage = 0.0
        self.__state = DEFAULT_PROPELLANT_GUN_MECHANIC_STATE

    @eventHandler
    def onComponentParamsCollected(self, params):
        self.__overchargeThreshold = params.maxOvercharge
        self.as_setupThresholdS(params.maxCharge / params.maxOvercharge)

    @eventHandler
    def onStatePrepared(self, state):
        self.__state = state
        self.__invalidateState(isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__state = state
        self.__invalidateState()

    @eventHandler
    def onStateTick(self, state):
        self.__state = state
        self.__invalidateProgress()

    @eventHandler
    def onMechanicCommand(self, command):
        self.as_activateHotKeyS(command.value)

    def onCurrentShellDamageChanged(self, newDamage):
        self.__shellDamage = newDamage
        self.__invalidateState(isInstantly=True)

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanic.PROPELLANT_GUN, self),
         VehicleMechanicPassengerUpdater(VehicleMechanic.PROPELLANT_GUN, self),
         VehicleMechanicCommandsUpdater(VehicleMechanic.PROPELLANT_GUN, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.PROPELLANT_GUN, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self),
         CurrentShellDamageUpdater(self),
         CrosshairTypeUpdater(self)]

    def __invalidateState(self, isInstantly=False):
        isMechanicApplied = self.__state.isUsableShell and self.__shellDamage > 0
        widgetState = self._GUI_STATE_MAP[self.__state.isOvercharge, isMechanicApplied]
        self.as_setStateS(widgetState, isInstantly)
        self.as_showHotKeysS(isShow=self.__state.isAvailable)
        self.__invalidateProgress()

    def __invalidateProgress(self):
        currentCharge = self.__state.currentCharge
        chargeProgress = currentCharge / self.__overchargeThreshold
        damage = self.__shellDamage * self.__state.getCurrentDamageFactor(currentCharge)
        self.as_setChargeValuesS(chargeProgress, damage)
