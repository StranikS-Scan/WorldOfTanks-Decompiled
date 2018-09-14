# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ParamsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ParamsMeta(BaseDAAPIComponent):

    def as_setValuesS(self, data):
        return self.flashObject.as_setValues(data) if self._isDAAPIInited() else None

    def as_highlightParamsS(self, type):
        return self.flashObject.as_highlightParams(type) if self._isDAAPIInited() else None
