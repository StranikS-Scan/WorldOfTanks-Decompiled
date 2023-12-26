# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_gift_entrypoint_model.py
from frameworks.wulf import ViewModel

class SurpriseGiftEntrypointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(SurpriseGiftEntrypointModel, self).__init__(properties=properties, commands=commands)

    def getRemainingTime(self):
        return self._getNumber(0)

    def setRemainingTime(self, value):
        self._setNumber(0, value)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(SurpriseGiftEntrypointModel, self)._initialize()
        self._addNumberProperty('remainingTime', 0)
        self._addBoolProperty('isAvailable', False)
        self.onClick = self._addCommand('onClick')
