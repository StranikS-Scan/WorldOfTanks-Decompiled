# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InputCheckerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class InputCheckerMeta(BaseDAAPIComponent):

    def sendUserInput(self, value, isValidSyntax):
        self._printOverrideError('sendUserInput')

    def as_setTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setTitle(value)

    def as_setBodyS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setBody(value)

    def as_setErrorMsgS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setErrorMsg(value)

    def as_setFormattedControlNumberS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setFormattedControlNumber(value)

    def as_setOriginalControlNumberS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setOriginalControlNumber(value)

    def as_invalidUserTextS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_invalidUserText(value)
