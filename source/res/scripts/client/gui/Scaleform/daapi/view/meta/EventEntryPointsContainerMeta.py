# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventEntryPointsContainerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventEntryPointsContainerMeta(BaseDAAPIComponent):

    def as_updateEntriesS(self, data):
        return self.flashObject.as_updateEntries(data) if self._isDAAPIInited() else None
