# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/awards_widget_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.collection_entry_point_view_model import CollectionEntryPointViewModel

class AwardsWidgetModel(ViewModel):
    __slots__ = ('onBpbitClick', 'onBpcoinClick', 'onTakeRewardsClick', 'showTankmen')

    def __init__(self, properties=8, commands=4):
        super(AwardsWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def collectionEntryPoint(self):
        return self._getViewModel(0)

    @staticmethod
    def getCollectionEntryPointType():
        return CollectionEntryPointViewModel

    def getBpbitCount(self):
        return self._getNumber(1)

    def setBpbitCount(self, value):
        self._setNumber(1, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(2)

    def setNotChosenRewardCount(self, value):
        self._setNumber(2, value)

    def getBpcoinCount(self):
        return self._getNumber(3)

    def setBpcoinCount(self, value):
        self._setNumber(3, value)

    def getIsBattlePassCompleted(self):
        return self._getBool(4)

    def setIsBattlePassCompleted(self, value):
        self._setBool(4, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(5)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(5, value)

    def getHasExtra(self):
        return self._getBool(6)

    def setHasExtra(self, value):
        self._setBool(6, value)

    def getIsSpecialVoiceTankmenEnabled(self):
        return self._getBool(7)

    def setIsSpecialVoiceTankmenEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(AwardsWidgetModel, self)._initialize()
        self._addViewModelProperty('collectionEntryPoint', CollectionEntryPointViewModel())
        self._addNumberProperty('bpbitCount', 0)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addNumberProperty('bpcoinCount', 0)
        self._addBoolProperty('isBattlePassCompleted', False)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self._addBoolProperty('hasExtra', False)
        self._addBoolProperty('isSpecialVoiceTankmenEnabled', False)
        self.onBpbitClick = self._addCommand('onBpbitClick')
        self.onBpcoinClick = self._addCommand('onBpcoinClick')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.showTankmen = self._addCommand('showTankmen')
