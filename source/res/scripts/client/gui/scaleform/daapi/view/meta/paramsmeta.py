# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ParamsMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ParamsMeta(DAAPIModule):

    def as_setValuesS(self, args):
        if self._isDAAPIInited():
            return self.flashObject.as_setValues(args)

    def as_highlightParamsS(self, type):
        if self._isDAAPIInited():
            return self.flashObject.as_highlightParams(type)
