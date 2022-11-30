# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_widget_resource_box_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.progress_reward_item_model import ProgressRewardItemModel

class NyWidgetResourceBoxModel(ViewModel):
    __slots__ = ('onGetReward', 'onStylePreview')

    def __init__(self, properties=6, commands=2):
        super(NyWidgetResourceBoxModel, self).__init__(properties=properties, commands=commands)

    def getMaxProgressValue(self):
        return self._getNumber(0)

    def setMaxProgressValue(self, value):
        self._setNumber(0, value)

    def getCurrentProgressValue(self):
        return self._getNumber(1)

    def setCurrentProgressValue(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ProgressRewardItemModel

    def getAvailableRewardsCount(self):
        return self._getNumber(3)

    def setAvailableRewardsCount(self, value):
        self._setNumber(3, value)

    def getReceivedRewardsCount(self):
        return self._getNumber(4)

    def setReceivedRewardsCount(self, value):
        self._setNumber(4, value)

    def getPointsForAwards(self):
        return self._getArray(5)

    def setPointsForAwards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPointsForAwardsType():
        return int

    def _initialize(self):
        super(NyWidgetResourceBoxModel, self)._initialize()
        self._addNumberProperty('maxProgressValue', 0)
        self._addNumberProperty('currentProgressValue', 0)
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('availableRewardsCount', 0)
        self._addNumberProperty('receivedRewardsCount', 0)
        self._addArrayProperty('pointsForAwards', Array())
        self.onGetReward = self._addCommand('onGetReward')
        self.onStylePreview = self._addCommand('onStylePreview')
