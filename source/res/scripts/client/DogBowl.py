# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DogBowl.py
from ClientSelectableObject import ClientSelectableObject
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class DogBowl(ClientSelectableObject):

    def onMouseClick(self):
        g_eventBus.handleEvent(events.HangarDogEvent(events.HangarDogEvent.ON_BOWL_CLICKED), scope=EVENT_BUS_SCOPE.LOBBY)
