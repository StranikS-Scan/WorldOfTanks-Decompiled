# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_intro_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BattlePassIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideo')

    def __init__(self, properties=2, commands=2):
        super(BattlePassIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getTankNames(self):
        return self._getArray(1)

    def setTankNames(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(BattlePassIntroViewModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addArrayProperty('tankNames', Array())
        self.onClose = self._addCommand('onClose')
        self.onVideo = self._addCommand('onVideo')
