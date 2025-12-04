# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/ny_progress_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_collections_rewards_model import NyCollectionsRewardsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_level_model import NyLevelModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class NyProgressViewModel(ViewModel):
    __slots__ = ('onClose', 'onGotoStore', 'onSelectVehicleDiscount')

    def __init__(self, properties=6, commands=3):
        super(NyProgressViewModel, self).__init__(properties=properties, commands=commands)

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

    def getProgressionLevel(self):
        return self._getNumber(3)

    def setProgressionLevel(self, value):
        self._setNumber(3, value)

    def getProgressionPoints(self):
        return self._getNumber(4)

    def setProgressionPoints(self, value):
        self._setNumber(4, value)

    def getProgressionLevels(self):
        return self._getArray(5)

    def setProgressionLevels(self, value):
        self._setArray(5, value)

    @staticmethod
    def getProgressionLevelsType():
        return NyLevelModel

    def _initialize(self):
        super(NyProgressViewModel, self)._initialize()
        self._addViewModelProperty('levelsRewards', NyLevelsRewardsModel())
        self._addViewModelProperty('collectionsRewards', NyCollectionsRewardsModel())
        self._addBoolProperty('isLevelsRewardsOpened', False)
        self._addNumberProperty('progressionLevel', 1)
        self._addNumberProperty('progressionPoints', 0)
        self._addArrayProperty('progressionLevels', Array())
        self.onClose = self._addCommand('onClose')
        self.onGotoStore = self._addCommand('onGotoStore')
        self.onSelectVehicleDiscount = self._addCommand('onSelectVehicleDiscount')
