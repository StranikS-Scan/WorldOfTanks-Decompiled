# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/battle_ability_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_levels_model import BattleAbilityTooltipLevelsModel
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_param_model import BattleAbilityTooltipParamModel

class BattleAbilityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BattleAbilityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getImageName(self):
        return self._getString(2)

    def setImageName(self, value):
        self._setString(2, value)

    def getIsPurchased(self):
        return self._getBool(3)

    def setIsPurchased(self, value):
        self._setBool(3, value)

    def getCharacteristics(self):
        return self._getArray(4)

    def setCharacteristics(self, value):
        self._setArray(4, value)

    @staticmethod
    def getCharacteristicsType():
        return BattleAbilityTooltipParamModel

    def getLevelsInfo(self):
        return self._getArray(5)

    def setLevelsInfo(self, value):
        self._setArray(5, value)

    @staticmethod
    def getLevelsInfoType():
        return BattleAbilityTooltipLevelsModel

    def _initialize(self):
        super(BattleAbilityTooltipModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addStringProperty('name', '')
        self._addStringProperty('imageName', '')
        self._addBoolProperty('isPurchased', False)
        self._addArrayProperty('characteristics', Array())
        self._addArrayProperty('levelsInfo', Array())
