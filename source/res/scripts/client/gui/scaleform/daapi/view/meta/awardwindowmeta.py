# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AwardWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class AwardWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onOKClick(self):
        self._printOverrideError('onOKClick')

    def onTakeNextClick(self):
        self._printOverrideError('onTakeNextClick')

    def onCloseClick(self):
        self._printOverrideError('onCloseClick')

    def onCheckBoxSelect(self, isSelected):
        self._printOverrideError('onCheckBoxSelect')

    def onWarningHyperlinkClick(self):
        self._printOverrideError('onWarningHyperlinkClick')

    def onAnimationStart(self):
        self._printOverrideError('onAnimationStart')

    def as_setDataS(self, data):
        """
        :param data: Represented by AwardWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTakeNextBtnS(self, texts):
        """
        :param texts: Represented by AwardWindowTakeNextBtnVO (AS)
        """
        return self.flashObject.as_setTakeNextBtn(texts) if self._isDAAPIInited() else None

    def as_startAnimationS(self):
        return self.flashObject.as_startAnimation() if self._isDAAPIInited() else None

    def as_endAnimationS(self):
        return self.flashObject.as_endAnimation() if self._isDAAPIInited() else None
