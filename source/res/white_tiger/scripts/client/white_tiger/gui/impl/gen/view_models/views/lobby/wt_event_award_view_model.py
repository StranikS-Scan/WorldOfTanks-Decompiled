# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_award_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.reward_item_model import RewardItemModel

class WtEventAwardViewModel(ViewModel):
    __slots__ = ('onAwardOpen',)

    def __init__(self, properties=7, commands=1):
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

    def getIsFinalReward(self):
        return self._getBool(3)

    def setIsFinalReward(self, value):
        self._setBool(3, value)

    def getIsBoxReward(self):
        return self._getBool(4)

    def setIsBoxReward(self, value):
        self._setBool(4, value)

    def getIsPostBattle(self):
        return self._getBool(5)

    def setIsPostBattle(self, value):
        self._setBool(5, value)

    def getIsEventAvailable(self):
        return self._getBool(6)

    def setIsEventAvailable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(WtEventAwardViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addStringProperty('title', '')
        self._addStringProperty('status', '')
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isBoxReward', False)
        self._addBoolProperty('isPostBattle', False)
        self._addBoolProperty('isEventAvailable', True)
        self.onAwardOpen = self._addCommand('onAwardOpen')
