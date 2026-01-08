# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/temp_overheat_gun_updater.py
from __future__ import absolute_import
import typing
import weakref
from events_handler import eventHandler
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater, ViewUpdatersCollection
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from Event import SafeEvent
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import IOverheatGunMechanicState
    from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import ITemperatureGunMechanicState

class ITemperatureOverheatGunStatesListenerLogic(object):

    def onOverheatStatePrepared(self, state):
        pass

    def onOverheatStateTransition(self, prevState, newState):
        pass

    def onTemperatureStatePrepared(self, state):
        pass

    def onTemperatureStateObservation(self, state):
        pass

    def onTemperatureStateTick(self, state):
        pass


class OverheatStatesBridge(VehicleMechanicStatesUpdater, IMechanicStatesListenerLogic):

    def __init__(self, onStatePrepared, onStateTransition):
        super(OverheatStatesBridge, self).__init__(VehicleMechanic.OVERHEAT_GUN, self)
        self.__onStatePrepared = weakref.proxy(onStatePrepared)
        self.__onStateTransition = weakref.proxy(onStateTransition)

    @eventHandler
    def onStatePrepared(self, state):
        self.__onStatePrepared(state)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__onStateTransition(prevState, newState)


class TemperatureStatesBridge(VehicleMechanicStatesUpdater, IMechanicStatesListenerLogic):

    def __init__(self, onStatePrepared, onStateObservation, onStateTick):
        super(TemperatureStatesBridge, self).__init__(VehicleMechanic.TEMPERATURE_GUN, self)
        self.__onStatePrepared = weakref.proxy(onStatePrepared)
        self.__onStateObservation = weakref.proxy(onStateObservation)
        self.__onStateTick = weakref.proxy(onStateTick)

    @eventHandler
    def onStatePrepared(self, state):
        self.__onStatePrepared(state)

    @eventHandler
    def onStateObservation(self, state):
        self.__onStateObservation(state)

    @eventHandler
    def onStateTick(self, state):
        self.__onStateTick(state)


class TemperatureOverheatGunStatesUpdater(ViewUpdater):

    def __init__(self, view):
        super(TemperatureOverheatGunStatesUpdater, self).__init__(view)
        self.onOverheatStatePrepared = self._createEvent()
        self.onOverheatStateTransition = self._createEvent()
        self.onTemperatureStatePrepared = self._createEvent()
        self.onTemperatureStateObservation = self._createEvent()
        self.onTemperatureStateTick = self._createEvent()
        self.__updatersCollection = ViewUpdatersCollection()

    def initialize(self):
        super(TemperatureOverheatGunStatesUpdater, self).initialize()
        self.view.subscribeTo(self)
        self.__updatersCollection.initialize(self._getViewUpdaters())

    def finalize(self):
        self.view.unsubscribeFrom(self)
        self.__updatersCollection.finalize()
        super(TemperatureOverheatGunStatesUpdater, self).finalize()

    def destroy(self):
        self.__updatersCollection.destroy()
        super(TemperatureOverheatGunStatesUpdater, self).destroy()

    def _getViewUpdaters(self):
        return [OverheatStatesBridge(self.onOverheatStatePrepared, self.onOverheatStateTransition), TemperatureStatesBridge(self.onTemperatureStatePrepared, self.onTemperatureStateObservation, self.onTemperatureStateTick)]
