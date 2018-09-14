# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SimpleWindowMeta(DAAPIModule):

    def onBtnClick(self, action):
        self._printOverrideError('onBtnClick')

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setTextS(self, header, descrition):
        if self._isDAAPIInited():
            return self.flashObject.as_setText(header, descrition)

    def as_setImageS(self, imgPath):
        if self._isDAAPIInited():
            return self.flashObject.as_setImage(imgPath)

    def as_setButtonsS(self, buttonsList, align, btnBottomMargin, btnWidth):
        if self._isDAAPIInited():
            return self.flashObject.as_setButtons(buttonsList, align, btnBottomMargin, btnWidth)
