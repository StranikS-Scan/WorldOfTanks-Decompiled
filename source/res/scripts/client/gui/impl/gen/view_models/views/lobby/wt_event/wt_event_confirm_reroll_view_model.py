# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_confirm_reroll_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.stats_model import StatsModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_model import RewardModel

class WtEventConfirmRerollViewModel(ViewModel):
    __slots__ = ('onReopen',)

    def __init__(self, properties=8, commands=1):
        super(WtEventConfirmRerollViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @property
    def stats(self):
        return self._getViewModel(1)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getWarningText(self):
        return self._getString(4)

    def setWarningText(self, value):
        self._setString(4, value)

    def getReopeningPrice(self):
        return self._getNumber(5)

    def setReopeningPrice(self, value):
        self._setNumber(5, value)

    def getCurrency(self):
        return self._getString(6)

    def setCurrency(self, value):
        self._setString(6, value)

    def getBoxId(self):
        return self._getString(7)

    def setBoxId(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(WtEventConfirmRerollViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('stats', StatsModel())
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('warningText', '')
        self._addNumberProperty('reopeningPrice', 25000)
        self._addStringProperty('currency', 'credits')
        self._addStringProperty('boxId', 'wt_hunter')
        self.onReopen = self._addCommand('onReopen')
