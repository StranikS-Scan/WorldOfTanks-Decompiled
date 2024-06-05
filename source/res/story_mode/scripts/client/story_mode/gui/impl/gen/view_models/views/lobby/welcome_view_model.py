# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/welcome_view_model.py
from frameworks.wulf import ViewModel

class WelcomeViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(WelcomeViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WelcomeViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self.onClose = self._addCommand('onClose')
