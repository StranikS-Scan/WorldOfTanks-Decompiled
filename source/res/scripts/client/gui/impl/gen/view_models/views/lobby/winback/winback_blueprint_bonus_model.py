# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/winback_blueprint_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.blueprint_bonus_model import BlueprintBonusModel

class WinbackBlueprintBonusModel(BlueprintBonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(WinbackBlueprintBonusModel, self).__init__(properties=properties, commands=commands)

    def getAmountInStorage(self):
        return self._getNumber(10)

    def setAmountInStorage(self, value):
        self._setNumber(10, value)

    def getIsSelected(self):
        return self._getBool(11)

    def setIsSelected(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(WinbackBlueprintBonusModel, self)._initialize()
        self._addNumberProperty('amountInStorage', 0)
        self._addBoolProperty('isSelected', False)
