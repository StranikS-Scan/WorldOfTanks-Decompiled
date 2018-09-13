# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/inputChecker/InputChecker.py
from gui.Scaleform.daapi.view.meta.InputCheckerMeta import InputCheckerMeta

class InputChecker(InputCheckerMeta):

    def __init__(self):
        super(InputChecker, self).__init__()
        self.__formattedControlNumber = None
        self.__originalControlNumber = None
        self.__controlNumber = None
        self.__questionTitle = 'defaultMessage'
        self.__questionBody = 'defaultMessage'
        self.__errorMsg = 'defaultErrorMessage'
        return

    def _populate(self):
        super(InputChecker, self)._populate()
        self.as_invalidUserTextS(False)

    def _dispose(self):
        super(InputChecker, self)._dispose()
        self.__formattedControlNumber = None
        self.__originalControlNumber = None
        self.__controlNumber = None
        self.__questionTitle = None
        self.__questionBody = None
        self.__errorMsg = None
        return

    def setControlNumbers(self, controlNumber, formatFunction = None):
        if self.__originalControlNumber != str(controlNumber):
            self.as_invalidUserTextS(False)
        if formatFunction is not None:
            self.__formattedControlNumber = formatFunction(controlNumber)
        else:
            self.__formattedControlNumber = controlNumber
        self.__originalControlNumber = str(controlNumber)
        self.as_setFormattedControlNumberS(self.__formattedControlNumber)
        self.as_setOriginalControlNumberS(self.__originalControlNumber)
        return

    def sendUserInput(self, value, isValidSyntax):
        if value == self.__originalControlNumber and isValidSyntax:
            self.as_invalidUserTextS(True)
        else:
            self.as_invalidUserTextS(False)

    @property
    def questionTitle(self):
        return self.__questionTitle

    @questionTitle.setter
    def questionTitle(self, value):
        self.__questionTitle = value
        self.as_setTitleS(self.__questionTitle)

    @property
    def questionBody(self):
        return self.__questionBody

    @questionBody.setter
    def questionBody(self, value):
        self.__questionBody = value
        self.as_setBodyS(self.__questionBody)

    @property
    def errorMsg(self):
        return self.__errorMsg

    @errorMsg.setter
    def errorMsg(self, value):
        self.__errorMsg = value
        self.as_setErrorMsgS(self.__errorMsg)
