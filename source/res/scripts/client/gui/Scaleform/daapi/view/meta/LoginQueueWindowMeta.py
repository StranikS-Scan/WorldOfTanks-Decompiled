# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LoginQueueWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LoginQueueWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onCancelClick(self):
        """
        :return :
        """
        self._printOverrideError('onCancelClick')

    def onAutoLoginClick(self):
        """
        :return :
        """
        self._printOverrideError('onAutoLoginClick')

    def as_setTitleS(self, title):
        """
        :param title:
        :return :
        """
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_setMessage(message) if self._isDAAPIInited() else None

    def as_setCancelLabelS(self, cancelLabel):
        """
        :param cancelLabel:
        :return :
        """
        return self.flashObject.as_setCancelLabel(cancelLabel) if self._isDAAPIInited() else None

    def as_showAutoLoginBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_showAutoLoginBtn(value) if self._isDAAPIInited() else None
