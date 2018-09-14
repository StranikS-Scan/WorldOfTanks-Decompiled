# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationProfileWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationProfileWindowMeta(DAAPIModule):

    def actionBtnClickHandler(self):
        self._printOverrideError('actionBtnClickHandler')

    def hyperLinkHandler(self, value):
        self._printOverrideError('hyperLinkHandler')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setFormationEmblemS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setFormationEmblem(value)

    def as_updateFormationInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateFormationInfo(data)

    def as_updateActionButtonS(self, lbl, enabled):
        if self._isDAAPIInited():
            return self.flashObject.as_updateActionButton(lbl, enabled)
