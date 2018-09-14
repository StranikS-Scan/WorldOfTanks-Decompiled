# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InputCheckerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class InputCheckerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def sendUserInput(self, value, isValidSyntax):
        """
        :param value:
        :param isValidSyntax:
        :return :
        """
        self._printOverrideError('sendUserInput')

    def as_setTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setBodyS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setBody(value) if self._isDAAPIInited() else None

    def as_setErrorMsgS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setErrorMsg(value) if self._isDAAPIInited() else None

    def as_setFormattedControlNumberS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setFormattedControlNumber(value) if self._isDAAPIInited() else None

    def as_setOriginalControlNumberS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setOriginalControlNumber(value) if self._isDAAPIInited() else None

    def as_invalidUserTextS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_invalidUserText(value) if self._isDAAPIInited() else None
