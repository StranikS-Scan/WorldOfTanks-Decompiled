# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/squad_bonus_item_renderer_model.py
from frameworks.wulf import ViewModel

class SquadBonusItemRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SquadBonusItemRendererModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getString(0)

    def setLevel(self, value):
        self._setString(0, value)

    def getDefeatValue(self):
        return self._getNumber(1)

    def setDefeatValue(self, value):
        self._setNumber(1, value)

    def getWinValue(self):
        return self._getNumber(2)

    def setWinValue(self, value):
        self._setNumber(2, value)

    def getIsCurrentLevel(self):
        return self._getBool(3)

    def setIsCurrentLevel(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SquadBonusItemRendererModel, self)._initialize()
        self._addStringProperty('level', '')
        self._addNumberProperty('defeatValue', 0)
        self._addNumberProperty('winValue', 0)
        self._addBoolProperty('isCurrentLevel', False)
