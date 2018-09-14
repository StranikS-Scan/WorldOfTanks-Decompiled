# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrequeueWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class PrequeueWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def requestToEnqueue(self):
        """
        :return :
        """
        self._printOverrideError('requestToEnqueue')

    def requestToLeave(self):
        """
        :return :
        """
        self._printOverrideError('requestToLeave')

    def showFAQWindow(self):
        """
        :return :
        """
        self._printOverrideError('showFAQWindow')

    def isEnqueueBtnEnabled(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isEnqueueBtnEnabled')

    def isLeaveBtnEnabled(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isLeaveBtnEnabled')

    def as_enableLeaveBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableLeaveBtn(value) if self._isDAAPIInited() else None

    def as_enableEnqueueBtnS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_enableEnqueueBtn(value) if self._isDAAPIInited() else None
