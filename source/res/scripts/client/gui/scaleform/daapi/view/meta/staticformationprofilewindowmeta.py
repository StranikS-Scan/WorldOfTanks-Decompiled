# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationProfileWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class StaticFormationProfileWindowMeta(AbstractWindowView):

    def actionBtnClickHandler(self, action):
        self._printOverrideError('actionBtnClickHandler')

    def onClickHyperLink(self, value):
        self._printOverrideError('onClickHyperLink')

    def as_setWindowSizeS(self, width, height):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowSize(width, height)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setFormationEmblemS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setFormationEmblem(value)

    def as_updateFormationInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateFormationInfo(data)

    def as_updateActionButtonS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateActionButton(data)

    def as_showViewS(self, idx):
        if self._isDAAPIInited():
            return self.flashObject.as_showView(idx)
