# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PhotoZone.py
from ClientSelectableObject import ClientSelectableObject

class PhotoZone(ClientSelectableObject):

    def onMouseClick(self):
        super(PhotoZone, self).onMouseClick()
        from gui.server_events.events_dispatcher import showMissionsMarathon
        showMissionsMarathon()
