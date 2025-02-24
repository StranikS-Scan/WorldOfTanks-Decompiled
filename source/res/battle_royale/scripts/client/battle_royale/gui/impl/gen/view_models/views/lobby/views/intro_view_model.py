# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/intro_view_model.py
from frameworks.wulf import ViewModel

class IntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowVideo')

    def __init__(self, properties=2, commands=2):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self.onClose = self._addCommand('onClose')
        self.onShowVideo = self._addCommand('onShowVideo')
