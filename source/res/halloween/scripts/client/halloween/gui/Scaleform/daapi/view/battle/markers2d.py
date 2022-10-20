# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/markers2d.py
import BigWorld
import Event
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from halloween.gui.shared.events import BuffGUIEvent

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
