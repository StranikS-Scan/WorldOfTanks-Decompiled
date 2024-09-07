# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/poll/poll_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PollViewType(Enum):
    SURVEY = 'survey'
    APPLICATION_FORM = 'application_form'


class PollViewModel(ViewModel):
    __slots__ = ('onGoToPoll', 'onWindowClose')

    def __init__(self, properties=5, commands=2):
        super(PollViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def getSubmitButtonLbl(self):
        return self._getString(2)

    def setSubmitButtonLbl(self, value):
        self._setString(2, value)

    def getCancelButtonLbl(self):
        return self._getString(3)

    def setCancelButtonLbl(self, value):
        self._setString(3, value)

    def getViewType(self):
        return PollViewType(self._getString(4))

    def setViewType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(PollViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('text', '')
        self._addStringProperty('submitButtonLbl', '')
        self._addStringProperty('cancelButtonLbl', '')
        self._addStringProperty('viewType')
        self.onGoToPoll = self._addCommand('onGoToPoll')
        self.onWindowClose = self._addCommand('onWindowClose')
