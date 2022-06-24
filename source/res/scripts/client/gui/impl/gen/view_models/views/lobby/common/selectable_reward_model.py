# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/selectable_reward_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_item_model import SelectableRewardItemModel
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_tab_model import SelectableRewardTabModel

class SelectableRewardModel(ViewModel):
    __slots__ = ('onOkClick', 'onCloseClick', 'onTabClick', 'onRewardAdd', 'onRewardReduce')

    def __init__(self, properties=4, commands=5):
        super(SelectableRewardModel, self).__init__(properties=properties, commands=commands)

    def getTabs(self):
        return self._getArray(0)

    def setTabs(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTabsType():
        return SelectableRewardTabModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return SelectableRewardItemModel

    def getTotalRewardCount(self):
        return self._getNumber(2)

    def setTotalRewardCount(self, value):
        self._setNumber(2, value)

    def getSelectedTab(self):
        return self._getString(3)

    def setSelectedTab(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(SelectableRewardModel, self)._initialize()
        self._addArrayProperty('tabs', Array())
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('totalRewardCount', 0)
        self._addStringProperty('selectedTab', '')
        self.onOkClick = self._addCommand('onOkClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onTabClick = self._addCommand('onTabClick')
        self.onRewardAdd = self._addCommand('onRewardAdd')
        self.onRewardReduce = self._addCommand('onRewardReduce')
