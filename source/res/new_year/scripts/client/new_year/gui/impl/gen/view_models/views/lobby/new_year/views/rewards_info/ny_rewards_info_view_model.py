# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/rewards_info/ny_rewards_info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_collections_rewards_model import NyCollectionsRewardsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_level_model import NyLevelModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class NyRewardsInfoViewModel(ViewModel):
    __slots__ = ('onFadeInDone', 'onGotoStore', 'onSelectVehicleDiscount')

    def __init__(self, properties=7, commands=3):
        super(NyRewardsInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def levelsRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getLevelsRewardsType():
        return NyLevelsRewardsModel

    @property
    def collectionsRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getCollectionsRewardsType():
        return NyCollectionsRewardsModel

    def getIsLevelsRewardsOpened(self):
        return self._getBool(2)

    def setIsLevelsRewardsOpened(self, value):
        self._setBool(2, value)

    def getIsFaded(self):
        return self._getBool(3)

    def setIsFaded(self, value):
        self._setBool(3, value)

    def getProgressionLevel(self):
        return self._getNumber(4)

    def setProgressionLevel(self, value):
        self._setNumber(4, value)

    def getProgressionPoints(self):
        return self._getNumber(5)

    def setProgressionPoints(self, value):
        self._setNumber(5, value)

    def getProgressionLevels(self):
        return self._getArray(6)

    def setProgressionLevels(self, value):
        self._setArray(6, value)

    @staticmethod
    def getProgressionLevelsType():
        return NyLevelModel

    def _initialize(self):
        super(NyRewardsInfoViewModel, self)._initialize()
        self._addViewModelProperty('levelsRewards', NyLevelsRewardsModel())
        self._addViewModelProperty('collectionsRewards', NyCollectionsRewardsModel())
        self._addBoolProperty('isLevelsRewardsOpened', False)
        self._addBoolProperty('isFaded', False)
        self._addNumberProperty('progressionLevel', 1)
        self._addNumberProperty('progressionPoints', 0)
        self._addArrayProperty('progressionLevels', Array())
        self.onFadeInDone = self._addCommand('onFadeInDone')
        self.onGotoStore = self._addCommand('onGotoStore')
        self.onSelectVehicleDiscount = self._addCommand('onSelectVehicleDiscount')
