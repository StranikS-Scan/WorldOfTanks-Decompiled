# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/auxiliary_rocket_launcher_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from BattleReplay import g_replayCtrl
from cache import last_cached_method
from constants import SECONDARY_GUN_STATE, UNKNOWN_GUN_INSTALLATION_INDEX
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.AuxiliaryRocketLauncherWidgetMeta import AuxiliaryRocketLauncherWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.shooting_updaters import IShootingReactionsView, ShootingReactionsUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from items.components.gun_installation_components import GunInstallationSlot
    from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher import AuxiliaryRocketLauncherState

class AuxiliaryRocketLauncherWidget(AuxiliaryRocketLauncherWidgetMeta, ContainersListener, IMechanicStatesListenerLogic, IShootingReactionsView):
    _AUXILIARY_ROCKET_LAUNCHER_UI_STATES = {SECONDARY_GUN_STATE.IDLE: MECHANICS_WIDGET_CONST.IDLE,
     SECONDARY_GUN_STATE.READY: {True: MECHANICS_WIDGET_CONST.DEPLOYING,
                                 False: MECHANICS_WIDGET_CONST.READY},
     SECONDARY_GUN_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     SECONDARY_GUN_STATE.COOLDOWN: MECHANICS_WIDGET_CONST.PREPARING,
     SECONDARY_GUN_STATE.DISABLED: {True: MECHANICS_WIDGET_CONST.DEPLOYING,
                                    False: MECHANICS_WIDGET_CONST.READY}}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_SPECIAL_ABILITY: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    def __init__(self):
        super(AuxiliaryRocketLauncherWidget, self).__init__()
        self.__installationIndex = UNKNOWN_GUN_INSTALLATION_INDEX
        self.__progressUpdaters = {}

    def onDiscreteShotsDone(self, gunInstallationSlot, isCurrentVehicle):
        if isCurrentVehicle and gunInstallationSlot.installationIndex == self.__installationIndex:
            self.as_shootDoneS()

    @eventHandler
    def onStatePrepared(self, state):
        self.__installationIndex = state.gunInstallationIndex
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(self.__getDisplayState(state), state.progress, state.timeLeft)

    def _populate(self):
        self.__progressUpdaters = {MECHANICS_WIDGET_CONST.PREPARING: self.as_setPreparingProgressS}
        super(AuxiliaryRocketLauncherWidget, self)._populate()

    def _dispose(self):
        super(AuxiliaryRocketLauncherWidget, self)._dispose()
        self.__progressUpdaters.clear()

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self),
         ShootingReactionsUpdater(self)]

    def __getDisplayState(self, state):
        displayState = self._AUXILIARY_ROCKET_LAUNCHER_UI_STATES[state.state]
        if state.isValidForAimingMode():
            displayState = displayState[state.isInAimingMode]
        return displayState

    def __invalidateAll(self, state, isInstantly=False):
        uiState = self.__getDisplayState(state)
        isInstantly = isInstantly or g_replayCtrl.isTimeWarpInProgress
        self.__invalidateProgress.reset()
        self.__invalidateProgress(uiState, state.progress, state.timeLeft)
        self.as_setStateS(uiState, isInstantly)

    @last_cached_method()
    def __invalidateProgress(self, uiState, progress, timeLeft):
        if uiState in self.__progressUpdaters:
            self.__progressUpdaters[uiState](progress)
        self.as_setTimeS(timeLeft)
