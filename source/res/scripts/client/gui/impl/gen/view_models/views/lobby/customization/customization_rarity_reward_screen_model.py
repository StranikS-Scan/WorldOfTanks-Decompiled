# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_rarity_reward_screen_model.py
from frameworks.wulf import ViewModel

class CustomizationRarityRewardScreenModel(ViewModel):
    __slots__ = ('goToExterior', 'goToGarage')

    def __init__(self, properties=5, commands=2):
        super(CustomizationRarityRewardScreenModel, self).__init__(properties=properties, commands=commands)

    def getIsFirstAttachment(self):
        return self._getBool(0)

    def setIsFirstAttachment(self, value):
        self._setBool(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def getRarity(self):
        return self._getString(3)

    def setRarity(self, value):
        self._setString(3, value)

    def getIsExteriorEnabled(self):
        return self._getBool(4)

    def setIsExteriorEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CustomizationRarityRewardScreenModel, self)._initialize()
        self._addBoolProperty('isFirstAttachment', False)
        self._addStringProperty('name', '')
        self._addStringProperty('title', '')
        self._addStringProperty('rarity', '')
        self._addBoolProperty('isExteriorEnabled', False)
        self.goToExterior = self._addCommand('goToExterior')
        self.goToGarage = self._addCommand('goToGarage')
