# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ParamsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ParamsMeta(BaseDAAPIComponent):

    def as_setValuesS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setValues(data)

    def as_highlightParamsS(self, type):
        if self._isDAAPIInited():
            return self.flashObject.as_highlightParams(type)
