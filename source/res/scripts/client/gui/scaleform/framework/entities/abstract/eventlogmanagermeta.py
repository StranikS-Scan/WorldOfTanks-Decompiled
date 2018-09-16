# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/EventLogManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventLogManagerMeta(BaseDAAPIComponent):

    def logEvent(self, subSystemType, eventType, uiid, arg):
        self._printOverrideError('logEvent')

    def as_setSystemEnabledS(self, isEnabled):
        return self.flashObject.as_setSystemEnabled(isEnabled) if self._isDAAPIInited() else None
