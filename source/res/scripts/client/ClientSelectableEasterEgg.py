# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableEasterEgg.py
from ClientSelectableObject import ClientSelectableObject
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class ClientSelectableEasterEgg(ClientSelectableObject):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ClientSelectableEasterEgg, self).__init__()
        if self.bootcampController.isInBootcamp():
            self.enable(False)

    def onClicked(self):
        super(ClientSelectableEasterEgg, self).onClicked()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AUTHORS_VIEW), EVENT_BUS_SCOPE.LOBBY)
