# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableMarathonHangarObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.server_events.events_dispatcher import showMissionsMarathon

class ClientSelectableMarathonHangarObject(ClientSelectableObject):

    def onMouseClick(self):
        super(ClientSelectableMarathonHangarObject, self).onMouseClick()
        showMissionsMarathon()
