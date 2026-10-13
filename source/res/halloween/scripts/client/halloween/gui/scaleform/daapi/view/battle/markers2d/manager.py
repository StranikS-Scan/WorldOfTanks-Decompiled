# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/markers2d/manager.py
from __future__ import absolute_import
import Event
from chat_commands_consts import INVALID_MARKER_ID, INVALID_MARKER_SUBTYPE, INVALID_TARGET_ID, MarkerType
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.framework import getSwfExtensionUrl
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import AreaMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import AreaMarker
from shared_utils import findFirst
from halloween.gui.scaleform.daapi.view.battle.markers2d.vehicle_plugins import HalloweenVehicleMarkerPlugin
from halloween.gui.scaleform.daapi.view.battle.markers2d.equipment_plugins import HalloweenEquipmentsMarkerPlugin

class HWAreaMarker(AreaMarker):

    def __init__(self, markerID, targetID=INVALID_TARGET_ID, bcMarkerType=MarkerType.INVALID_MARKER_TYPE, active=True):
        super(HWAreaMarker, self).__init__(markerID, targetID, bcMarkerType, active)
        self.subType = INVALID_MARKER_SUBTYPE
        self._hasAnimation = False

    def setMarkerSubType(self, subType):
        self.subType = subType

    def hasAnimation(self):
        return self._hasAnimation

    def setHasAnimation(self, value):
        self._hasAnimation = value


class HalloweenAreaMarkerPlugin(AreaMarkerPlugin):

    def __init__(self, parentObj, clazz=HWAreaMarker):
        super(HalloweenAreaMarkerPlugin, self).__init__(parentObj, clazz)
        self.onReplyFeedbackReceived = Event.Event()

    def stop(self):
        self.onReplyFeedbackReceived.clear()
        super(HalloweenAreaMarkerPlugin, self).stop()

    def setMarkerAlwaysSticky(self, uniqueID):
        marker = self.markers.get(uniqueID)
        if marker:
            self._parentObj.setAlwaysStickyMarkerId(marker.getMarkerID())

    def removeMarkerAlwaysSticky(self, uniqueID):
        marker = self.markers.get(uniqueID)
        if marker:
            self._parentObj.removeAlwaysStickyMarkerId(marker.getMarkerID())

    def getMarkerSubtype(self, targetID):
        if targetID == INVALID_MARKER_ID:
            return INVALID_MARKER_SUBTYPE
        marker = findFirst(lambda item: item.getTargetID() == targetID, self.markers.values())
        return INVALID_MARKER_SUBTYPE if not marker else marker.subType

    def setMarkerSubType(self, uniqueID, subType):
        marker = self.markers.get(uniqueID)
        if marker:
            marker.setMarkerSubType(subType)

    def setHasAnimation(self, uniqueID, value):
        marker = self.markers.get(uniqueID)
        if marker:
            marker.setHasAnimation(value)

    def _onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        super(HalloweenAreaMarkerPlugin, self)._onReplyFeedbackReceived(targetID, replierID, markerType, oldReplyCount, newReplyCount)
        cID, marker = self._getComponent(targetID, markerType)
        isSticky = newReplyCount > 0
        if marker is not None and marker.getIsSticky() != isSticky:
            self.onReplyFeedbackReceived(cID, isSticky)
        return

    def _setMarkerRepliesAndCheckState(self, marker, count, isTargetForPlayer, checkState=True):
        markerID = marker.getMarkerID()
        oldReplyCount = marker.getReplyCount()
        if isTargetForPlayer:
            if marker.getIsRepliedByPlayer():
                isRepliedByPlayer = count >= oldReplyCount
            else:
                isRepliedByPlayer = count > oldReplyCount
            marker.setIsRepliedByPlayer(isRepliedByPlayer)
            if marker.hasAnimation() and oldReplyCount == 0 and count == 0:
                self._parentObj.invokeMarker(markerID, 'triggerClickAnimation')
        if oldReplyCount != count and (oldReplyCount == 0 or count == 0):
            self._setMarkerReplied(marker, count > 0)
        self._setMarkerReplyCount(marker, count)
        if checkState:
            self._checkNextState(marker)

    def _getComponent(self, targetID, markerType):
        return findFirst(lambda item: item[1].getTargetID() == targetID and item[1].getBCMarkerType() == markerType, self.markers.items(), (0, None))


class HalloweenMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = getSwfExtensionUrl('halloween', 'halloweenBattleVehicleMarkersApp.swf')

    def __init__(self):
        super(HalloweenMarkersManager, self).__init__()
        self.alwaysIsSticky = set()

    def setAlwaysStickyMarkerId(self, markerId):
        self.alwaysIsSticky.add(markerId)

    def removeAlwaysStickyMarkerId(self, markerId):
        self.alwaysIsSticky.discard(markerId)

    def setMarkerSticky(self, markerID, isSticky):
        isAlwaysSticky = markerID in self.alwaysIsSticky
        if self.isStickyEnabled and self.isIBCEnabled or isAlwaysSticky:
            self.canvas.markerSetSticky(markerID, isSticky or isAlwaysSticky)

    def _setupPlugins(self, arenaVisitor):
        setup = super(HalloweenMarkersManager, self)._setupPlugins(arenaVisitor)
        setup.update({'area_markers': HalloweenAreaMarkerPlugin,
         'vehicles': HalloweenVehicleMarkerPlugin,
         'equipments': HalloweenEquipmentsMarkerPlugin})
        return setup

    def _updateMarkerStickyState(self, isSticky):
        if not isSticky:
            for markerId in self.markerIds:
                if markerId in self.alwaysIsSticky:
                    continue
                self.canvas.markerSetSticky(markerId, False)
