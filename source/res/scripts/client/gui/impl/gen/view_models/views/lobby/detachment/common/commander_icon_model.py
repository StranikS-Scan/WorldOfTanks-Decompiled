# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/commander_icon_model.py
from frameworks.wulf import ViewModel

class CommanderIconModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CommanderIconModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def getIsUnique(self):
        return self._getBool(2)

    def setIsUnique(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CommanderIconModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isUnique', False)
