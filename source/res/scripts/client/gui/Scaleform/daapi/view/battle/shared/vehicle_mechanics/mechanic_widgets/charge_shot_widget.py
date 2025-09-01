# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/charge_shot_widget.py
import typing
import CommandMapping
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.ChargeShotWidgetMeta import ChargeShotWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanic_life_cycle_view_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.current_shell_damage_updater import CurrentShellDamageUpdater
from gui.veh_mechanics.battle.updaters.shot_blocked_upater import ShotBlockedUpdater
from vehicles.components.component_life_cycle import IComponentLifeCycleListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events.events_listener import ComponentListener
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from _weakref import ProxyType
    from ChargeShotComponent import ChargeShotState, ChargeShotComponent
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class ChargeShotMechanicWidget(ChargeShotWidgetMeta, ComponentListener, IMechanicStatesListenerLogic, IComponentLifeCycleListener):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    def __init__(self):
        super(ChargeShotMechanicWidget, self).__init__()
        self.__damageFactorsPerLevel = None
        self.__expectedDamage = 0
        self.__baseDamage = 0
        self.__level = 0
        return

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, oldState, newState):
        if oldState.hasShotBlock != newState.hasShotBlock:
            self.as_setShootBlockS(newState.hasShotBlock)
        self.__invalidateAll(newState)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(state)

    @eventHandler
    def onComponentParamsCollected(self, component):
        params = component.params
        if params is None:
            return
        else:
            self.__damageFactorsPerLevel = params.damageFactorsPerLevel
            self.__invalidateExpectedDamage(self.__baseDamage)
            return

    def onCurrentShellDamageChanged(self, newDamage):
        self.__invalidateExpectedDamage(newDamage)

    def onShotBlocked(self, error):
        if error == CANT_SHOOT_ERROR.CHARGE_SHOT_BLOCKING:
            self.as_showShootBlockAnimationS()

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanic.CHARGE_SHOT, self),
         VehicleMechanicPassengerUpdater(VehicleMechanic.CHARGE_SHOT, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.CHARGE_SHOT, self),
         HotKeysViewUpdater(self._HOT_KEY_MAP.keys(), self),
         CurrentShellDamageUpdater(self),
         ShotBlockedUpdater(self)]

    def __invalidateAll(self, state, isInstantly=False):
        if state.hasCharging:
            uiState = MECHANICS_WIDGET_CONST.PREPARING
        elif state.hasShotBlock:
            uiState = MECHANICS_WIDGET_CONST.DISABLE
        elif state.canStart:
            uiState = MECHANICS_WIDGET_CONST.READY
        else:
            uiState = MECHANICS_WIDGET_CONST.IDLE
        self.__invalidateProgress(state)
        self.as_setStateS(uiState, isInstantly)
        self.__invalidateExpectedDamage(self.__baseDamage)

    def __invalidateProgress(self, state):
        self.__level = state.level
        if state.hasCharging:
            timeLeft = state.timeLeft()
            self.as_setUpdateProgressS(state.level, state.progress(timeLeft))
            self.as_setTimeS(timeLeft)
            return
        elif state.hasShotBlock:
            self.as_setTimeS(state.timeLeft())
            return
        else:
            self.as_setTimeS(None)
            return

    def __updateExpectedDamage(self, newBaseDamage=None):
        if newBaseDamage is None:
            newBaseDamage = self.__baseDamage
        self.__baseDamage = newBaseDamage
        factors = self.__damageFactorsPerLevel
        newExpectedDamage = newBaseDamage if factors is None else round(factors[self.__level] * newBaseDamage)
        if self.__expectedDamage != newExpectedDamage:
            self.__expectedDamage = newExpectedDamage
            return True
        else:
            return False

    def __invalidateExpectedDamage(self, newDamage):
        if self.__updateExpectedDamage(newDamage):
            self.as_setDamageS(self.__expectedDamage)
