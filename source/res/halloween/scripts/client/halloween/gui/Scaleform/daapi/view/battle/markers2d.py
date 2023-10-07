# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/markers2d.py
from collections import defaultdict
import BigWorld
import Event
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from halloween.gui.shared.events import BuffGUIEvent
_STATUS_EFFECTS_PRIORITY = ((BATTLE_MARKER_STATES.HW_DEBUFF_STATE,), (BATTLE_MARKER_STATES.STUN_STATE,))

class HWMarkersManager(MarkersManager):

    def __init__(self, *args):
        super(HWMarkersManager, self).__init__(*args)
        self.__earlyEvents = []
        self.__eManager = Event.EventManager()
        self.onVehicleBuffMarkerUpdated = Event.Event(self.__eManager)
        self.addListener(BuffGUIEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(BuffGUIEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _populate(self):
        super(HWMarkersManager, self)._populate()
        if self.__earlyEvents:
            for vehicleID, componentID, iconName in self.__earlyEvents:
                self.onVehicleBuffMarkerUpdated(vehicleID, componentID, iconName)

        self.__earlyEvents = None
        return

    def _dispose(self):
        self.removeListener(BuffGUIEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(BuffGUIEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        super(HWMarkersManager, self)._dispose()

    def _setupPlugins(self, arenaVisitor):
        setup = super(HWMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = HWMarkersPlugin
        return setup

    def __handleBuffUnApply(self, event):
        self.__onBuffGUIEvent(event, False)

    def __handleBuffApply(self, event):
        self.__onBuffGUIEvent(event, True)

    def __onBuffGUIEvent(self, event, isApplied):
        eventCtx = event.ctx
        vehicleID = eventCtx['vehicleID']
        player = BigWorld.player()
        if player and player.playerVehicleID == vehicleID:
            return
        else:
            buffName = eventCtx['id']
            if self.__earlyEvents is not None:
                self.__earlyEvents.append((vehicleID, buffName, isApplied))
            else:
                self.onVehicleBuffMarkerUpdated(vehicleID, buffName, isApplied)
            return


class HWMarkersPlugin(RespawnableVehicleMarkerPlugin):

    def __init__(self, parentObject, *args):
        super(HWMarkersPlugin, self).__init__(parentObject, *args)
        self.__vehicleMarkerIcons = {}
        self.__markersStatesExtended = defaultdict(list)

    def start(self):
        super(HWMarkersPlugin, self).start()
        self._parentObj.onVehicleBuffMarkerUpdated += self.__onVehicleBuffMarkerUpdated

    def stop(self):
        self._parentObj.onVehicleBuffMarkerUpdated -= self.__onVehicleBuffMarkerUpdated
        super(HWMarkersPlugin, self).stop()

    def _getMarkerSymbol(self, vehicleID):
        pass

    def __onVehicleBuffMarkerUpdated(self, vehicleID, iconName, isApplied):
        marker = self._markers.get(vehicleID)
        if not marker:
            return
        else:
            markerId = marker.getMarkerID()
            if isApplied:
                self.__vehicleMarkerIcons[vehicleID] = iconName
                self._invokeMarker(markerId, 'showBuff', iconName)
            else:
                currentIconName = self.__vehicleMarkerIcons.get(vehicleID, None)
                if currentIconName == iconName:
                    del self.__vehicleMarkerIcons[vehicleID]
                    self._invokeMarker(markerId, 'hideBuff')
            return

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(HWMarkersPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if vehicleID not in self._markers:
            return
        handle = self._markers[vehicleID].getMarkerID()
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER:
            self.__updateMarker(vehicleID, handle, **value)
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self._hideVehicleMarker(vehicleID)
            self._destroyVehicleMarker(vehicleID)

    def __updateMarker(self, vehicleID, handle, isShown, isSourceVehicle, duration, animated, markerID):
        self._updateStatusMarkerState(vehicleID, isShown, handle, markerID, duration, animated, isSourceVehicle)

    def _updateStatusMarkerState(self, vehicleID, isShown, handle, markerID, duration, animated, isSourceVehicle, blinkAnim=True):
        extendedStatuses = self.__markersStatesExtended[vehicleID]
        if isShown and not self.__statusInActive(vehicleID, markerID):
            hasNeighbor = self.__hasNeighborInPrioritizes
            extendedStatuses.append((markerID, -BigWorld.serverTime() if hasNeighbor(markerID) else 0.0))
            self.__markersStatesExtended[vehicleID] = extendedStatuses
        elif not isShown and self.__statusInActive(vehicleID, markerID):
            self._removeState(vehicleID, markerID)
        if self.__markersStatesExtended[vehicleID]:
            activeStatuses = sorted(self.__markersStatesExtended[vehicleID], key=lambda x: (x[1], self._getMarkerStatusPriority(x[0])))
            self.__markersStatesExtended[vehicleID] = activeStatuses
        self._markersStates[vehicleID] = [ state for state, _ in self.__markersStatesExtended[vehicleID] ]
        currentlyActiveStatusID = self._markersStates[vehicleID][0] if self._markersStates[vehicleID] else -1
        if markerID == BATTLE_MARKER_STATES.STUN_STATE:
            isSourceVehicle = True
        elif markerID == BATTLE_MARKER_STATES.DEBUFF_STATE:
            isSourceVehicle = False
        if isShown:
            self._invokeMarker(handle, 'showStatusMarker', markerID, self._getMarkerStatusPriority(markerID), isSourceVehicle, duration, currentlyActiveStatusID, self._getMarkerStatusPriority(currentlyActiveStatusID), animated, blinkAnim)
        else:
            self._invokeMarker(handle, 'hideStatusMarker', markerID, currentlyActiveStatusID, animated)

    def _removeState(self, vehicleID, state):
        super(HWMarkersPlugin, self)._removeState(vehicleID, state)
        for data in self.__markersStatesExtended[vehicleID]:
            if data[0] == state:
                self.__markersStatesExtended[vehicleID].remove(data)
                return

    def __statusInActive(self, vehicleID, statusID):
        for status, _ in self.__markersStatesExtended[vehicleID]:
            if status == statusID:
                return True

        return False

    def __hasNeighborInPrioritizes(self, statusID):
        for statuses in _STATUS_EFFECTS_PRIORITY:
            if statusID in statuses and len(statuses) > 1:
                return True

        return False

    def _getMarkerStatusPriority(self, statusID):
        try:
            for index, priorities in enumerate(_STATUS_EFFECTS_PRIORITY):
                if statusID in priorities:
                    return index

        except ValueError:
            return -1

        return super(HWMarkersPlugin, self)._getMarkerStatusPriority(statusID)
