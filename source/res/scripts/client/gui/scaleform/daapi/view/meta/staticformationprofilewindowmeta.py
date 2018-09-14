# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationProfileWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class StaticFormationProfileWindowMeta(AbstractWindowView):

    def actionBtnClickHandler(self, action):
        self._printOverrideError('actionBtnClickHandler')

    def onClickHyperLink(self, value):
        self._printOverrideError('onClickHyperLink')

    def as_setWindowSizeS(self, width, height):
        return self.flashObject.as_setWindowSize(width, height) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setFormationEmblemS(self, value):
        return self.flashObject.as_setFormationEmblem(value) if self._isDAAPIInited() else None

    def as_updateFormationInfoS(self, data):
        return self.flashObject.as_updateFormationInfo(data) if self._isDAAPIInited() else None

    def as_updateActionButtonS(self, data):
        return self.flashObject.as_updateActionButton(data) if self._isDAAPIInited() else None

    def as_showViewS(self, idx):
        return self.flashObject.as_showView(idx) if self._isDAAPIInited() else None
