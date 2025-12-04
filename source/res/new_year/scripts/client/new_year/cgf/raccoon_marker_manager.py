# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/raccoon_marker_manager.py
import CGF
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import onAddedQuery
from helpers import dependency
from helpers.events_handler import EventsHandler
from new_year.skeletons.new_year import ITamagotchiDataProvider

@registerComponent
class RaccoonLobbyMarker(object):
    domain = CGF.DomainOption.DomainClient


class RaccoonMarkerManager(CGF.ComponentManager, EventsHandler):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    @onAddedQuery(CGF.GameObject, RaccoonLobbyMarker)
    def handleMarkerAdded(self, go, _):
        if self._dataProvider.raccoonState:
            for child in CGF.HierarchyManager(self.spaceID).getChildrenIncludingInactive(go):
                child.activate()

    def _getEvents(self):
        return ((self._dataProvider.onRaccoonStateUpdated, self._onRaccoonStateUpdated),)

    def _onRaccoonStateUpdated(self, value):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        for go, _ in CGF.Query(self.spaceID, (CGF.GameObject, RaccoonLobbyMarker)):
            for child in hierarchyManager.getChildrenIncludingInactive(go):
                if value:
                    child.activate()
                child.deactivate()
