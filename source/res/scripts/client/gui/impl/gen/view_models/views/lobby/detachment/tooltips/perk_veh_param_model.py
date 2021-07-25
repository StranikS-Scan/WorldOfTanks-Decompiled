# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/perk_veh_param_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PerkVehParamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PerkVehParamModel, self).__init__(properties=properties, commands=commands)

    def getBonus(self):
        return self._getString(0)

    def setBonus(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIsPermanent(self):
        return self._getBool(3)

    def setIsPermanent(self, value):
        self._setBool(3, value)

    def getIsPenalty(self):
        return self._getBool(4)

    def setIsPenalty(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PerkVehParamModel, self)._initialize()
        self._addStringProperty('bonus', '')
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('description', '')
        self._addBoolProperty('isPermanent', False)
        self._addBoolProperty('isPenalty', False)
