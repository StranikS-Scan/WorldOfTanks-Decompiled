# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableEasterEgg.py
from ClientSelectableObject import ClientSelectableObject
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE

class ClientSelectableEasterEgg(ClientSelectableObject):

    def onClicked(self):
        super(ClientSelectableEasterEgg, self).onClicked()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AUTHORS_VIEW), EVENT_BUS_SCOPE.LOBBY)
