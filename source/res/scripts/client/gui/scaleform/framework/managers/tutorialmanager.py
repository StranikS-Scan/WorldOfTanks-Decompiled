# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TutorialManager.py
from Event import Event, EventManager
from gui.Scaleform.framework.entities.abstract.TutorialManagerMeta import TutorialManagerMeta

class ScaleformTutorialManager(TutorialManagerMeta):

    def __init__(self):
        super(ScaleformTutorialManager, self).__init__()
        self.__eventMgr = EventManager()
        self.onComponentFoundEvent = Event(self.__eventMgr)
        self.onComponentDisposedEvent = Event(self.__eventMgr)
        self.onTriggerActivatedEvent = Event(self.__eventMgr)
        self.onEffectCompletedEvent = Event(self.__eventMgr)

    def _dispose(self):
        self.__eventMgr.clear()
        super(ScaleformTutorialManager, self)._dispose()

    def onComponentFound(self, componentId, viewTutorialId):
        self.onComponentFoundEvent(componentId, viewTutorialId)

    def onTriggerActivated(self, componentId, triggerId, state):
        self.onTriggerActivatedEvent(componentId, triggerId, state)

    def onComponentDisposed(self, componentId):
        self.onComponentDisposedEvent(componentId)

    def onEffectCompleted(self, componentId, effectType):
        self.onEffectCompletedEvent(componentId, effectType)
