# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_berlin_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.secret_event.reward_model import RewardModel

class ActionBerlinModel(ActionMenuModel):
    __slots__ = ('onBuyPack',)

    def __init__(self, properties=12, commands=4):
        super(ActionBerlinModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(4)

    @property
    def rewardList(self):
        return self._getViewModel(5)

    def getIsStarted(self):
        return self._getBool(6)

    def setIsStarted(self, value):
        self._setBool(6, value)

    def getCountdownDaysLeft(self):
        return self._getNumber(7)

    def setCountdownDaysLeft(self, value):
        self._setNumber(7, value)

    def getCountdownTime(self):
        return self._getNumber(8)

    def setCountdownTime(self, value):
        self._setNumber(8, value)

    def getShowPack(self):
        return self._getBool(9)

    def setShowPack(self, value):
        self._setBool(9, value)

    def getPackTimer(self):
        return self._getNumber(10)

    def setPackTimer(self, value):
        self._setNumber(10, value)

    def getPackDayLeft(self):
        return self._getNumber(11)

    def setPackDayLeft(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(ActionBerlinModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('rewardList', UserListModel())
        self._addBoolProperty('isStarted', False)
        self._addNumberProperty('countdownDaysLeft', 0)
        self._addNumberProperty('countdownTime', 0)
        self._addBoolProperty('showPack', False)
        self._addNumberProperty('packTimer', 0)
        self._addNumberProperty('packDayLeft', 0)
        self.onBuyPack = self._addCommand('onBuyPack')
