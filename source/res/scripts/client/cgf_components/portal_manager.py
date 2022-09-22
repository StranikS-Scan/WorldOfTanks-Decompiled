# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/portal_manager.py
import CGF
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_components import IsSelected, IsHighlighted
from EventPortal import EventPortal
from EventVehicle import EventVehicle
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.wt_event.wt_event_helpers import g_execute_after_all_event_vehicles_loaded
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.prebattle_vehicle import IPrebattleVehicle
from helpers import dependency

class PortalSelectionManager(CGF.ComponentManager):
    gameEvent = dependency.descriptor(IEventBattlesController)
    prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    hangarSpace = dependency.descriptor(IHangarSpace)
    portalQuery = CGF.QueryConfig(EventPortal, CGF.GameObject)
    vehicleQuery = CGF.QueryConfig(EventVehicle, CGF.GameObject)
    selectedQuery = CGF.QueryConfig(CGF.GameObject, EventVehicle, IsSelected)
    highlightedQuery = CGF.QueryConfig(CGF.GameObject, IsHighlighted)

    def activate(self):
        if self.hangarSpace.spaceInited:
            self.__onSpaceCreated()
        else:
            self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.PORTAL_MANAGER_ACTIVATED), scope=EVENT_BUS_SCOPE.LOBBY)

    def deactivate(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated

    @onAddedQuery(IsSelected, EventVehicle)
    def onVehicleSelected(self, _, vehicle):
        self.prebattleVehicle.switchCamera(vehicle)

    @onAddedQuery(IsSelected, EventPortal)
    def onPortalSelected(self, _, __):
        self.__removeHighlight()

    @onRemovedQuery(IsSelected, EventPortal)
    def onPortalDeselected(self, _, __):
        self.__removeHighlight()
        self.__removeSelection()

    @onAddedQuery(IsHighlighted, EventVehicle)
    def onVehicleHighlighted(self, _, entity):
        if not entity.isDestroyed:
            entity.setHighlight(True, fallback=True)

    @onRemovedQuery(IsHighlighted, EventVehicle)
    def onVehicleFaded(self, _, entity):
        if not entity.isDestroyed:
            entity.setHighlight(False, fallback=True)

    @onAddedQuery(IsHighlighted, EventPortal)
    def onPortalHighlighted(self, _, entity):
        if not self.gameEvent.isEventPrbActive():
            for _, gameObject in self.vehicleQuery:
                if gameObject.findComponentByType(IsHighlighted) is None:
                    gameObject.createComponent(IsHighlighted)

            if not entity.isDestroyed:
                entity.setHighlight(True, fallback=True)
        return

    @onRemovedQuery(IsHighlighted, EventPortal)
    def onPortalFaded(self, _, entity):
        for _, gameObject in self.vehicleQuery:
            gameObject.removeComponentByType(IsHighlighted)

        if not entity.isDestroyed:
            entity.setHighlight(False, fallback=True)

    @g_execute_after_all_event_vehicles_loaded
    def __onSpaceCreated(self):
        if self.gameEvent.isEventPrbActive():
            self.prebattleVehicle.selectAny()

    def __removeHighlight(self):
        for go, _ in self.highlightedQuery:
            go.removeComponentByType(IsHighlighted)

    def __removeSelection(self):
        for go, _, __ in self.selectedQuery:
            go.removeComponentByType(IsSelected)
