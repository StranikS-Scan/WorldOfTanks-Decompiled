# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/lootboxes_intro_model.py
from frameworks.wulf import ViewModel

class LootboxesIntroModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LootboxesIntroModel, self).__init__(properties=properties, commands=commands)

    def getBoxCount(self):
        return self._getNumber(0)

    def setBoxCount(self, value):
        self._setNumber(0, value)

    def getBonusQuestBoxCount(self):
        return self._getNumber(1)

    def setBonusQuestBoxCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(LootboxesIntroModel, self)._initialize()
        self._addNumberProperty('boxCount', 0)
        self._addNumberProperty('bonusQuestBoxCount', 0)
