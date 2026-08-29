# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/vehicle_component.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import createComponentLifeCycleEvents, ILifeCycleComponent
from events_handler import eventHandler, EventsQuery
from PlayerEvents import g_playerEvents
from shared_utils import skipInEditor
from vehicle_appearance.constants import AppearanceState
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle
from vehicles.entities.vehicle_events import IVehicleEventsListenerLogic
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from events_containers.components.life_cycle import IComponentLifeCycleEvents
    from Vehicle import Vehicle
    from vehicle_systems.CompoundAppearance import CompoundAppearance
_logger = logging.getLogger(__name__)

class VehicleDynamicComponent(ReplicableDynamicScriptComponent, ILifeCycleComponent, EventsQuery, ContainersListener, IVehicleEventsListenerLogic):
    EVENTS_PROPERTY_NAME = 'events'
    APPEARANCE_READY_STATE = AppearanceState.CONSTRUCTED

    @skipInEditor
    def __init__(self):
        super(VehicleDynamicComponent, self).__init__()
        self.__appearanceReady = self.__componentDestroyed = False
        self.__lifeCycleEvents = createComponentLifeCycleEvents(self)
        self.lateSubscribeTo(self._getEvents(self.entity))

    @property
    def lifeCycleEvents(self):
        return self.__lifeCycleEvents

    def isAppearanceReady(self):
        return self.__appearanceReady

    def isComponentDestroyed(self):
        return self.__componentDestroyed

    def isPlayerVehicle(self, player):
        return self.__isAvatarReady(player) and self.entity.id == player.playerVehicleID

    def isObservedVehicle(self, player, vehicle):
        return self.__isAvatarReady(player) and vehicle is not None and self.entity.id == vehicle.id

    def onDestroy(self):
        if self.__componentDestroyed:
            return
        self._unsubscribeFromEvents(self._getEvents(self.entity))
        self.__appearanceReady = False
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__componentDestroyed = True
        self.__lifeCycleEvents.destroy()

    def onLeaveWorld(self):
        self.onDestroy()

    @eventHandler
    def onAppearanceReady(self):
        if self.__appearanceReadyState() == AppearanceState.CONSTRUCTED:
            self.__processAppearanceReady()

    @eventHandler
    def onAppearanceComponentsReady(self):
        if self.__appearanceReadyState() == AppearanceState.COMPONENTS_CREATED:
            self.__processAppearanceReady()

    @eventHandler
    @ifAppearanceReady
    def onAppearanceReset(self):
        self._onAppearanceReset()
        self.__lifeCycleEvents.processAppearanceReset()
        self.__appearanceReady = False

    @eventHandler
    @ifAppearanceReady
    def onSiegeStateUpdated(self, newState, timeToNextMode):
        self._collectComponentParams(self.entity.typeDescriptor)
        self.__lifeCycleEvents.processParamsCollected()
        self._updateComponentAvatar()

    def _initComponent(self):
        self.__initComponentAppearance()
        self.__initComponentAvatar()

    def _onAppearanceReady(self):
        self._collectComponentParams(self.entity.typeDescriptor)
        self.__lifeCycleEvents.processParamsCollected()

    def _onAppearanceReset(self):
        pass

    def _onAvatarReady(self, player):
        pass

    def _onComponentAppearanceUpdate(self, **kwargs):
        pass

    def _onComponentAvatarUpdate(self, player):
        pass

    def _collectComponentParams(self, typeDescriptor):
        pass

    @ifPlayerVehicle
    def _updateComponentAvatar(self, player=None):
        self._onComponentAvatarUpdate(player)

    @ifAppearanceReady
    def _updateComponentAppearance(self, **kwargs):
        self._onComponentAppearanceUpdate(**kwargs)

    def __initComponentAvatar(self):
        if self.__isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __initComponentAppearance(self):
        if self.__isAppearanceReady():
            self.__processAppearanceReady()

    def __isAvatarReady(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.userSeesWorld()

    def __isAppearanceReady(self):
        appearance = self.entity.appearance
        return appearance is not None and appearance.state >= self.__appearanceReadyState() and appearance.isActualVehicle(self.entity)

    @ifPlayerVehicle
    def __onAvatarReady(self, player=None):
        self._onAvatarReady(player)
        self.__lifeCycleEvents.processComponentAvatarReady()
        self._onComponentAvatarUpdate(player)

    def __processAppearanceReady(self):
        if self.__appearanceReady:
            return
        self._onAppearanceReady()
        self.__appearanceReady = True
        self.__lifeCycleEvents.processAppearanceReady()
        self._onComponentAppearanceUpdate()

    @classmethod
    def __appearanceReadyState(cls):
        return cls.APPEARANCE_READY_STATE
