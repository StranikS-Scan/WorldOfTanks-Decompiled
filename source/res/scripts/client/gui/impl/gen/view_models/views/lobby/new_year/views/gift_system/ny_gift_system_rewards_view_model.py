# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/ny_gift_system_rewards_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class State(IntEnum):
    FORSELF = 0
    ONEGIFT = 1
    MULTIGIFTS = 2
    PROGRESSIONGIFT = 3


class NyGiftSystemRewardsViewModel(ViewModel):
    __slots__ = ('onOpenOneGift', 'onOpenGifts')

    def __init__(self, properties=8, commands=2):
        super(NyGiftSystemRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getState(self):
        return State(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getUserName(self):
        return self._getString(2)

    def setUserName(self, value):
        self._setString(2, value)

    def getUserClanAbbrev(self):
        return self._getString(3)

    def setUserClanAbbrev(self, value):
        self._setString(3, value)

    def getCongratulation(self):
        return self._getString(4)

    def setCongratulation(self, value):
        self._setString(4, value)

    def getGiftCount(self):
        return self._getNumber(5)

    def setGiftCount(self, value):
        self._setNumber(5, value)

    def getIsServerError(self):
        return self._getBool(6)

    def setIsServerError(self, value):
        self._setBool(6, value)

    def getIsOpeningBoxEnabled(self):
        return self._getBool(7)

    def setIsOpeningBoxEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NyGiftSystemRewardsViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('state')
        self._addStringProperty('userName', '')
        self._addStringProperty('userClanAbbrev', '')
        self._addStringProperty('congratulation', '')
        self._addNumberProperty('giftCount', 0)
        self._addBoolProperty('isServerError', False)
        self._addBoolProperty('isOpeningBoxEnabled', False)
        self.onOpenOneGift = self._addCommand('onOpenOneGift')
        self.onOpenGifts = self._addCommand('onOpenGifts')
