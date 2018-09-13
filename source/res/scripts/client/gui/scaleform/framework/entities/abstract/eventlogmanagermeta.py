# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/EventLogManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class EventLogManagerMeta(DAAPIModule):

    def logEvent(self, subSystemType, eventType, uiid, arg):
        self._printOverrideError('logEvent')
