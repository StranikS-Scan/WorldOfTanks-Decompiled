# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableRacingHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.marathon.racing_event import RacingEvent
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController

class ClientSelectableRacingHangarObject(ClientSelectableObject):
    _marathonEventsController = dependency.descriptor(IMarathonEventsController)

    def onMouseClick(self):
        super(ClientSelectableRacingHangarObject, self).onMouseClick()
        if self._marathonEventsController.isAnyActive():
            showMissionsMarathon(marathonPrefix=RacingEvent.RACING_MARATHON_PREFIX)
