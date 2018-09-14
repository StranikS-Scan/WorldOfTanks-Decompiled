# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SimpleWindowMeta(AbstractWindowView):

    def onBtnClick(self, action):
        self._printOverrideError('onBtnClick')

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setTextS(self, header, descrition):
        if self._isDAAPIInited():
            return self.flashObject.as_setText(header, descrition)

    def as_setImageS(self, imgPath, imgBottomMargin):
        if self._isDAAPIInited():
            return self.flashObject.as_setImage(imgPath, imgBottomMargin)

    def as_setButtonsS(self, buttonsList, align, btnWidth):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtons(buttonsList, align, btnWidth)
