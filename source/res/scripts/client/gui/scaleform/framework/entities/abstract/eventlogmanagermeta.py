# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/EventLogManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class EventLogManagerMeta(BaseDAAPIModule):

    def logEvent(self, subSystemType, eventType, uiid, arg):
        self._printOverrideError('logEvent')
