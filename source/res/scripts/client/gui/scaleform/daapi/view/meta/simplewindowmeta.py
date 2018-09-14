# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SimpleWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SimpleWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onBtnClick(self, action):
        """
        :param action:
        :return :
        """
        self._printOverrideError('onBtnClick')

    def as_setWindowTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, header, descrition):
        """
        :param header:
        :param descrition:
        :return :
        """
        return self.flashObject.as_setText(header, descrition) if self._isDAAPIInited() else None

    def as_setImageS(self, imgPath, imgBottomMargin):
        """
        :param imgPath:
        :param imgBottomMargin:
        :return :
        """
        return self.flashObject.as_setImage(imgPath, imgBottomMargin) if self._isDAAPIInited() else None

    def as_setButtonsS(self, buttonsList, align, btnWidth):
        """
        :param buttonsList:
        :param align:
        :param btnWidth:
        :return :
        """
        return self.flashObject.as_setButtons(buttonsList, align, btnWidth) if self._isDAAPIInited() else None
