# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/for_gift_blueprint_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.blueprint_bonus_model import BlueprintBonusModel

class ForGiftBlueprintBonusModel(BlueprintBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ForGiftBlueprintBonusModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(9)

    def setNation(self, value):
        self._setString(9, value)

    def getAmountInHangar(self):
        return self._getNumber(10)

    def setAmountInHangar(self, value):
        self._setNumber(10, value)

    def getAmountOfBluePrints(self):
        return self._getNumber(11)

    def setAmountOfBluePrints(self, value):
        self._setNumber(11, value)

    def getIsSelected(self):
        return self._getBoolean(12)

    def setIsSelected(self, value):
        self._setBoolean(12, value)

    def _initialize(self):
        super(ForGiftBlueprintBonusModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addNumberProperty('amountInHangar', 0)
        self._addNumberProperty('amountOfBluePrints', 0)
        self._addBooleanProperty('isSelected')
