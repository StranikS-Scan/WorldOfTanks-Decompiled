# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID

class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def init(self, *args):
        super(EventVehicleMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        super(EventVehicleMarkerPlugin, self).fini()
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self._markers:
            if eventID == _EVENT_ID.VEHICLE_SHOW_MESSAGE:
                handle = self._markers[vehicleID].getMarkerID()
                self.__showActionMassage(handle, *value)

    def __showActionMassage(self, handle, massage, isAlly):
        self._invokeMarker(handle, 'showActionMessage', massage, isAlly)
