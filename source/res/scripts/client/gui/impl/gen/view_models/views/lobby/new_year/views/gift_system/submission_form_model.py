# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/submission_form_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.friend_model import FriendModel

class SubmissionState(Enum):
    NONE = 'none'
    GIFT_SENDING = 'giftSending'
    PREV_GIFT_SENDING = 'prevGiftSending'
    LIMITS_LOADING = 'limitsLoading'
    BALANCE_UNAVAILABLE = 'balanceUnavailable'
    NO_LONGER_FRIEND = 'noLongerFriend'


class SubmissionFormModel(ViewModel):
    __slots__ = ('onRollCongrats', 'onSelectFriend', 'onSendAnimationEnd', 'onSendGift')
    NOT_SELECTED_SPA_ID = 0

    def __init__(self, properties=6, commands=4):
        super(SubmissionFormModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedFriend(self):
        return self._getViewModel(0)

    def getState(self):
        return SubmissionState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getSendPrice(self):
        return self._getNumber(2)

    def setSendPrice(self, value):
        self._setNumber(2, value)

    def getCongratsText(self):
        return self._getResource(3)

    def setCongratsText(self, value):
        self._setResource(3, value)

    def getFullfilledFriends(self):
        return self._getArray(4)

    def setFullfilledFriends(self, value):
        self._setArray(4, value)

    def getWaitingFriends(self):
        return self._getArray(5)

    def setWaitingFriends(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(SubmissionFormModel, self)._initialize()
        self._addViewModelProperty('selectedFriend', FriendModel())
        self._addStringProperty('state')
        self._addNumberProperty('sendPrice', 1)
        self._addResourceProperty('congratsText', R.invalid())
        self._addArrayProperty('fullfilledFriends', Array())
        self._addArrayProperty('waitingFriends', Array())
        self.onRollCongrats = self._addCommand('onRollCongrats')
        self.onSelectFriend = self._addCommand('onSelectFriend')
        self.onSendAnimationEnd = self._addCommand('onSendAnimationEnd')
        self.onSendGift = self._addCommand('onSendGift')
