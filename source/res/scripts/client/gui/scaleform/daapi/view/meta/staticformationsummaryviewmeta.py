# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationSummaryViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StaticFormationSummaryViewMeta(BaseDAAPIComponent):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
