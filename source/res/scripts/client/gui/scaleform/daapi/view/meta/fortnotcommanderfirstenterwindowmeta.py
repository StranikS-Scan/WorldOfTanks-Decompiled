# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortNotCommanderFirstEnterWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortNotCommanderFirstEnterWindowMeta(AbstractWindowView):

    def as_setTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setTitle(value)

    def as_setTextS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setText(value)

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setButtonLblS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtonLbl(value)
