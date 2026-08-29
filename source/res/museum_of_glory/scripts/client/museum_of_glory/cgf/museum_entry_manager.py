# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/cgf/museum_entry_manager.py
import typing
import CGF
import constants
from cgf_components import marker_component as lobbyMarkers
from cgf_components.hover_component import SelectionComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from helpers.cgf_utils import toggleCgfComponent
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IMuseumOfGloryController
if not constants.IS_EDITOR:
    from museum_of_glory.gui.window_events import showMuseumVehicleView
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
    from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LobbyVehicleMarkerView
    from cgf_components.marker_component import LobbyFlashMarker

@registerComponent
class MuseumLobbyMarker(object):
    domain = CGF.DomainOption.DomainClient


@registerComponent
class MuseumLobbyEntry(object):
    domain = CGF.DomainOption.DomainClient


def _createMuseumOfGloryMarker(lobbyView, markerId, _):
    return lobbyView.as_createCustomMarkerS(markerId, '', str(backport.text(R.strings.museum_of_glory.marker.entry())), '')


def initMuseumOfGloryMarker():
    lobbyMarkers.MARKER_CREATORS[lobbyMarkers.MarkerType.MUSEUM_OF_GLORY] = _createMuseumOfGloryMarker


class MuseumEntryManager(CGF.ComponentManager, EventsHandler):
    __mogController = dependency.descriptor(IMuseumOfGloryController)

    def activate(self):
        self._subscribe()
        self.__updateAllEntries()

    def deactivate(self):
        self._unsubscribe()

    @onAddedQuery(CGF.GameObject, MuseumLobbyEntry, SelectionComponent)
    def handleOutlineAdded(self, go, _, selectionComponent):
        selectionComponent.onClickAction += self.__onMuseumEntryClick
        self.__updateEntrySelection(go)

    @onRemovedQuery(MuseumLobbyEntry, SelectionComponent)
    def handleOutlineRemoved(self, _, selectionComponent):
        selectionComponent.onClickAction -= self.__onMuseumEntryClick

    @onAddedQuery(CGF.GameObject, MuseumLobbyMarker)
    def handleMarkerAdded(self, go, _):
        self.__updateMarkerChildren(go)

    def _getEvents(self):
        return ((self.__mogController.onConfigUpdate, self.__onMuseumConfigUpdate),)

    def __onMuseumEntryClick(self):
        if self.__mogController.isEnabled:
            showMuseumVehicleView()

    def __onMuseumConfigUpdate(self):
        self.__updateAllEntries()

    def __updateAllEntries(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        for go, _ in CGF.Query(self.spaceID, (CGF.GameObject, MuseumLobbyMarker)):
            self.__updateMarkerChildren(go, hierarchyManager)

        for go, _ in CGF.Query(self.spaceID, (CGF.GameObject, MuseumLobbyEntry)):
            self.__updateEntrySelection(go)

    def __updateMarkerChildren(self, go, hierarchyManager=None):
        hierarchyManager = hierarchyManager or CGF.HierarchyManager(self.spaceID)
        for child in hierarchyManager.getChildrenIncludingInactive(go):
            if self.__mogController.isEnabled:
                child.activate()
            child.deactivate()

    def __updateEntrySelection(self, go):
        toggleCgfComponent(go, SelectionComponent, self.__mogController.isEnabled)
