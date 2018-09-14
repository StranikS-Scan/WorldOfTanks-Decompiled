# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SimpleWindowMeta(AbstractWindowView):

    def onBtnClick(self, action):
        self._printOverrideError('onBtnClick')

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, header, descrition):
        return self.flashObject.as_setText(header, descrition) if self._isDAAPIInited() else None

    def as_setImageS(self, imgPath, imgBottomMargin):
        return self.flashObject.as_setImage(imgPath, imgBottomMargin) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonsList, align, btnWidth):
        """
        :param buttonsList: Represented by Vector.<SimpleWindowBtnVo> (AS)
        """
        return self.flashObject.as_setButtons(buttonsList, align, btnWidth) if self._isDAAPIInited() else None
