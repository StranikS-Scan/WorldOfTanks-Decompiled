# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_vehicle_capture_points_ctrl.py
from interfaces import IBattleController
from Event import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class EventVehicleCapturePointsController(IBattleController):
    __slots__ = ('onVehiclePointsChanged',)

    def __init__(self):
        super(EventVehicleCapturePointsController, self).__init__()
        self.onVehiclePointsChanged = Event()

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_VEHICLE_CAPTURE_POINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.onVehiclePointsChanged.clear()
