# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_box_reward_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_model import RewardModel
from gui.impl.gen.view_models.views.lobby.wt_event.vehicle_model import VehicleModel

class WtEventBoxRewardViewModel(ViewModel):
    __slots__ = ('onGoToStorage', 'showHangar', 'goToCollection', 'goToBuyBox', 'onClose')

    def __init__(self, properties=11, commands=5):
        super(WtEventBoxRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @property
    def additionalRewards(self):
        return self._getViewModel(1)

    @property
    def vehicle(self):
        return self._getViewModel(2)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getIsVehicleReward(self):
        return self._getBool(5)

    def setIsVehicleReward(self, value):
        self._setBool(5, value)

    def getIsSpecialBox(self):
        return self._getBool(6)

    def setIsSpecialBox(self, value):
        self._setBool(6, value)

    def getIsCollectionItem(self):
        return self._getBool(7)

    def setIsCollectionItem(self, value):
        self._setBool(7, value)

    def getIsCollectionCollected(self):
        return self._getBool(8)

    def setIsCollectionCollected(self, value):
        self._setBool(8, value)

    def getBoxCount(self):
        return self._getNumber(9)

    def setBoxCount(self, value):
        self._setNumber(9, value)

    def getBoxId(self):
        return self._getString(10)

    def setBoxId(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(WtEventBoxRewardViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('isVehicleReward', False)
        self._addBoolProperty('isSpecialBox', False)
        self._addBoolProperty('isCollectionItem', False)
        self._addBoolProperty('isCollectionCollected', False)
        self._addNumberProperty('boxCount', 0)
        self._addStringProperty('boxId', '')
        self.onGoToStorage = self._addCommand('onGoToStorage')
        self.showHangar = self._addCommand('showHangar')
        self.goToCollection = self._addCommand('goToCollection')
        self.goToBuyBox = self._addCommand('goToBuyBox')
        self.onClose = self._addCommand('onClose')
