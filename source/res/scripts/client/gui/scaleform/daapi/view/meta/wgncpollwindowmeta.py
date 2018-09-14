# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WGNCPollWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class WGNCPollWindowMeta(AbstractWindowView):

    def onBtnClick(self):
        self._printOverrideError('onBtnClick')

    def onLinkClick(self, actions):
        self._printOverrideError('onLinkClick')

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setTextS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setText(value)

    def as_setButtonLblS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonLbl(value)
