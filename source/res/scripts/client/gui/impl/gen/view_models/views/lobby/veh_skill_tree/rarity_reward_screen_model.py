# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/rarity_reward_screen_model.py
from frameworks.wulf import ViewModel

class RarityRewardScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(RarityRewardScreenModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getRarity(self):
        return self._getString(2)

    def setRarity(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(RarityRewardScreenModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('title', '')
        self._addStringProperty('rarity', '')
        self.onClose = self._addCommand('onClose')
