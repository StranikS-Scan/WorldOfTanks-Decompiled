# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardWindowMeta.py
from gui.Scaleform.daapi.view.lobby.award_window_base import AwardWindowBase

class AwardWindowMeta(AwardWindowBase):

    def onOKClick(self):
        self._printOverrideError('onOKClick')

    def onTakeNextClick(self):
        self._printOverrideError('onTakeNextClick')

    def onCloseClick(self):
        self._printOverrideError('onCloseClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
