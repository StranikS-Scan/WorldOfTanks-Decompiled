# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_award_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_item_model import RewardItemModel

class WtEventAwardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(WtEventAwardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getStatus(self):
        return self._getString(2)

    def setStatus(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getIsFinalReward(self):
        return self._getBool(4)

    def setIsFinalReward(self, value):
        self._setBool(4, value)

    def getIsPostBattle(self):
        return self._getBool(5)

    def setIsPostBattle(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(WtEventAwardViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addStringProperty('title', '')
        self._addStringProperty('status', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isPostBattle', False)
