# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventHelpWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class EventHelpWindowMeta(View):

    def as_setEventInfoPanelDataS(self, data):
        return self.flashObject.as_setEventInfoPanelData(data) if self._isDAAPIInited() else None
