# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/autoreloader_surge_widget.py
from __future__ import absolute_import, division
import typing
import CommandMapping
from constants import ARENA_PERIOD, AUTORELOADER_SURGE_RESTRICTION, AUTORELOADER_SURGE_STATE
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.AutoreloaderSurgeWidgetMeta import AutoreloaderSurgeWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.crosshair_type_updater import CrosshairTypeUpdater
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_life_cycle_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand, VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from typing import List
    from AutoreloaderSurgeController import AutoreloaderSurgeState
    from items.components.shared_components import AutoreloaderSurgeParams
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
_STATE_MAP = {AUTORELOADER_SURGE_STATE.IN_USE: MECHANICS_WIDGET_CONST.ACTIVE,
 AUTORELOADER_SURGE_STATE.MAX_CHARGES: MECHANICS_WIDGET_CONST.READY}

class AutoreloaderSurgeMechanicWidget(AutoreloaderSurgeWidgetMeta, ContainersListener, IComponentLifeCycleListenerLogic, IMechanicStatesListenerLogic):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_SPECIAL_ABILITY: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AutoreloaderSurgeMechanicWidget, self).__init__()
        self.__maxCharges = 0
        self.__startCharges = 0
        self.__chargeTimeSFullClip = 0.0
        self.__chargeTimeSRegular = 0.0
        self.__isPrebattle = False

    @eventHandler
    def onComponentParamsCollected(self, params):
        self.__maxCharges = int(params.maxCharges)
        self.__chargeTimeSFullClip = params.chargeTimeSFullClip
        self.__chargeTimeSRegular = params.chargeTimeSRegular
        self.__startCharges = int(params.startCharges)
        self.as_setSectorCountS(self.__maxCharges)
        if self.__isPrebattle:
            self.as_setTimeS(self.__chargeTimeSRegular)

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    @eventHandler
    def onStateTransition(self, _, newState):
        self.__invalidateAll(newState)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateAll(state)

    def _populate(self):
        super(AutoreloaderSurgeMechanicWidget, self)._populate()
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            self.__onArenaPeriodChange(arena.period)
        return

    def _dispose(self):
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(AutoreloaderSurgeMechanicWidget, self)._dispose()
        return

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanic.AUTORELOADER_SURGE, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.AUTORELOADER_SURGE, self),
         VehicleMechanicPassengerUpdater(VehicleMechanic.AUTORELOADER_SURGE, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self),
         CrosshairTypeUpdater(self)]

    def __onArenaPeriodChange(self, arenaPeriod, *_):
        isPrebattle = arenaPeriod < ARENA_PERIOD.BATTLE
        if self.__isPrebattle and not isPrebattle:
            self.as_setTimeS(0)
        elif isPrebattle and self.__chargeTimeSRegular > 0:
            self.as_setTimeS(self.__chargeTimeSRegular)
        self.__isPrebattle = isPrebattle

    def __getReloadTimeLeft(self):
        snapshot = self.__sessionProvider.shared.ammo.getPartiallyReloadingClipState()
        return snapshot.getBaseValue() - snapshot.getTimePassed()

    def __getWidgetState(self, state):
        mapped = _STATE_MAP.get(state.state)
        if mapped:
            return mapped
        if state.state == AUTORELOADER_SURGE_STATE.CHARGING:
            if state.ncharges > 0:
                return MECHANICS_WIDGET_CONST.READY
            return MECHANICS_WIDGET_CONST.PREPARING
        return MECHANICS_WIDGET_CONST.DISABLE

    def __buildStagesProgress(self, state):
        ncharges = int(state.ncharges)
        filling = min(self.__maxCharges - ncharges, 1)
        emptyCount = max(0, self.__maxCharges - ncharges - filling)
        return [1.0] * ncharges + [state.progress] * filling + [0.0] * emptyCount

    def __invalidateAll(self, state, isInstantly=False):
        if self.__isPrebattle:
            ncharges = self.__startCharges
            widgetState = MECHANICS_WIDGET_CONST.READY if ncharges > 0 else MECHANICS_WIDGET_CONST.PREPARING
            self.as_setChargeCountS(ncharges)
            self.as_setStateS(widgetState, isInstantly)
            self.as_setAvailableS(False)
            self.as_setBoostedChargeS(False)
            self.as_setStagesProgressS([1.0] * ncharges + [0.0] * (self.__maxCharges - ncharges))
            return
        widgetState = self.__getWidgetState(state)
        if widgetState == MECHANICS_WIDGET_CONST.ACTIVE:
            self.as_setTimeS(self.__getReloadTimeLeft())
        else:
            self.as_setTimeS(state.chargeTime * (1.0 - state.progress))
        isAvailable = state.restrictions == AUTORELOADER_SURGE_RESTRICTION.NO_RESTRICTION
        isBoosted = state.state == AUTORELOADER_SURGE_STATE.CHARGING and self.__chargeTimeSFullClip > 0 and state.chargeTime <= self.__chargeTimeSFullClip
        self.as_setChargeCountS(state.ncharges)
        self.as_setStateS(widgetState, isInstantly)
        self.as_setAvailableS(isAvailable)
        self.as_setBoostedChargeS(isBoosted)
        self.as_setStagesProgressS(self.__buildStagesProgress(state))
