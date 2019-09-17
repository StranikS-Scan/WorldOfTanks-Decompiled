# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_race_position_ctrl.py
from interfaces import IBattleController
from Event import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class EventRacePositionController(IBattleController):
    __slots__ = ('onRacePositionsUpdate', 'onRaceFinished', 'onRaceFirstLights', 'onRaceLastLights')

    def __init__(self):
        super(EventRacePositionController, self).__init__()
        self.onRacePositionsUpdate = Event()
        self.onRaceFinished = Event()
        self.onRaceFirstLights = Event()
        self.onRaceLastLights = Event()

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_RACE_POSITION

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.onRacePositionsUpdate.clear()
        self.onRaceFinished.clear()
        self.onRaceFirstLights.clear()
        self.onRaceLastLights.clear()
