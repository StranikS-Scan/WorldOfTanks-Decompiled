# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/reward_path_card_view_model.py
from frameworks.wulf import ViewModel

class RewardPathCardViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(RewardPathCardViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getMaxProgress(self):
        return self._getNumber(1)

    def setMaxProgress(self, value):
        self._setNumber(1, value)

    def getCertificates(self):
        return self._getNumber(2)

    def setCertificates(self, value):
        self._setNumber(2, value)

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def getIsStoryChoiceState(self):
        return self._getBool(4)

    def setIsStoryChoiceState(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(RewardPathCardViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('certificates', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isStoryChoiceState', False)
        self.onClick = self._addCommand('onClick')
