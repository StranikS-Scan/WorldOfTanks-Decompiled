# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/skeletons/event_controller.py
from skeletons.gui.game_control import IGameController

class IEventController(IGameController):

    def isEnabled(self):
        raise NotImplementedError

    def getEventStartTime(self):
        raise NotImplementedError

    def getEventFinishTime(self):
        raise NotImplementedError
