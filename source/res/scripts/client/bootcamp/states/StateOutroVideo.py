# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateOutroVideo.py
from AbstractState import AbstractState
from bootcamp.states import STATE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus

class StateOutroVideo(AbstractState):

    def __init__(self):
        super(StateOutroVideo, self).__init__(STATE.OUTRO_VIDEO)

    def handleKeyEvent(self, event):
        pass

    def _doActivate(self):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO, None, {'video': 'video/_bootcampFinish.usm'}), EVENT_BUS_SCOPE.LOBBY)
        return

    def _doDeactivate(self):
        pass
