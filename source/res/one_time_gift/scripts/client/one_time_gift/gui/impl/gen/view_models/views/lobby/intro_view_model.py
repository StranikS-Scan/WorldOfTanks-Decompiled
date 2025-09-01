# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/intro_view_model.py
from frameworks.wulf import ViewModel

class IntroViewModel(ViewModel):
    __slots__ = ('onShowVideo', 'onContinue', 'onClose')

    def __init__(self, properties=2, commands=3):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    def getEndTime(self):
        return self._getNumber(0)

    def setEndTime(self, value):
        self._setNumber(0, value)

    def getShowAnimation(self):
        return self._getBool(1)

    def setShowAnimation(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addNumberProperty('endTime', 0)
        self._addBoolProperty('showAnimation', False)
        self.onShowVideo = self._addCommand('onShowVideo')
        self.onContinue = self._addCommand('onContinue')
        self.onClose = self._addCommand('onClose')
