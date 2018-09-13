# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/TutorialControl.py
from gui.Scaleform.daapi.view.meta.TutorialControlMeta import TutorialControlMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
__author__ = 'a_ushyutsau'

class TutorialControl(TutorialControlMeta, DAAPIModule):

    def __init__(self):
        super(TutorialControl, self).__init__()

    def _populate(self):
        super(TutorialControl, self)._populate()
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.UI_CONTROL_ADDED), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _dispose(self):
        super(TutorialControl, self)._dispose()
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.UI_CONTROL_REMOVED), scope=EVENT_BUS_SCOPE.GLOBAL)

    def restart(self):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.RESTART), scope=EVENT_BUS_SCOPE.GLOBAL)

    def refuse(self):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.REFUSE), scope=EVENT_BUS_SCOPE.GLOBAL)
