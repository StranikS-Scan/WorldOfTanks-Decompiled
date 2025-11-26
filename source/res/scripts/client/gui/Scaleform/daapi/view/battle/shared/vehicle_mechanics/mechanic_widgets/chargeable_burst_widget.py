# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/chargeable_burst_widget.py
import typing
from gui.Scaleform.daapi.view.meta.ChargeableBurstWidgetMeta import ChargeableBurstWidgetMeta
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events import ComponentListener
from events_handler import eventHandler
if typing.TYPE_CHECKING:
    from ChargeableBurstComponent import ChargeableBurstModeState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot

class ChargeableBurstMechanicWidget(ChargeableBurstWidgetMeta, ComponentListener, IMechanicStatesListenerLogic):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @eventHandler
    def onStatePrepared(self, state):
        self.as_setupS(state.penetrationCount, state.burstCount)
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateMode(newState)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateCharges(state)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.CHARGEABLE_BURST, self), VehicleMechanicStatesUpdater(VehicleMechanic.CHARGEABLE_BURST, self)]

    def _populate(self):
        super(ChargeableBurstMechanicWidget, self)._populate()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsUpdated += self.__onShellsUpdated
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
            ammoCtrl.onCurrentShellReset += self.__onCurrentShellReset
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        return

    def _dispose(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsUpdated -= self.__onShellsUpdated
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
            ammoCtrl.onCurrentShellReset -= self.__onCurrentShellReset
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        super(ChargeableBurstMechanicWidget, self)._dispose()
        return

    def __onShellsUpdated(self, intCD, quantity, quantityInClip, result):
        self.__invalidateShells()

    def __onCurrentShellChanged(self, intCD):
        self.__invalidateShells()

    def __onCurrentShellReset(self):
        self.__invalidateShells()

    def __onGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        self.as_updateBurstReloadingStateS(not state.isReloadingFinished())

    def __invalidateAll(self, state, isInstantly=False):
        self.__invalidateMode(state, isInstantly)
        self.__invalidateCharges(state, isInstantly)

    def __invalidateMode(self, state, isInstantly=False):
        if state.isBurstActive:
            self.__invalidateShells()
        self.as_setModeS(state.isBurstActive, isInstantly)

    def __invalidateCharges(self, state, isInstantly=False):
        self.as_setChargesS(state.charges, state.shots, isInstantly)

    def __invalidateShells(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        quantity, _ = ammoCtrl.getCurrentShells()
        self.as_setShellsQuantityLeftS(quantity)
