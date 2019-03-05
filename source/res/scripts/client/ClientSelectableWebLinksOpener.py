# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableWebLinksOpener.py
from ClientSelectableObject import ClientSelectableObject
from gui.shared import g_eventBus, events

class ClientSelectableWebLinksOpener(ClientSelectableObject):

    def onMouseClick(self):
        super(ClientSelectableWebLinksOpener, self).onMouseClick()
        if self.url:
            g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PARSED, url=self.url))
