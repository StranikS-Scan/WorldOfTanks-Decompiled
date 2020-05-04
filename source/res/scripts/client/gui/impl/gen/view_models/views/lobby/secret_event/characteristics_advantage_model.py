# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/characteristics_advantage_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CharacteristicsAdvantageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CharacteristicsAdvantageModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getText(self):
        return self._getResource(2)

    def setText(self, value):
        self._setResource(2, value)

    def getCharName(self):
        return self._getString(3)

    def setCharName(self, value):
        self._setString(3, value)

    def getPrefix(self):
        return self._getString(4)

    def setPrefix(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(CharacteristicsAdvantageModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('text', R.invalid())
        self._addStringProperty('charName', '')
        self._addStringProperty('prefix', '')
