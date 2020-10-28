# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventQuestsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventQuestsPanelMeta(BaseDAAPIComponent):

    def onQuestPanelClick(self):
        self._printOverrideError('onQuestPanelClick')

    def as_setListDataProviderS(self, data):
        return self.flashObject.as_setListDataProvider(data) if self._isDAAPIInited() else None
