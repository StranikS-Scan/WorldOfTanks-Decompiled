# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/fill_envelope_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.friend_model import FriendModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.reward_view_model import RewardViewModel

class EnvelopeType(IntEnum):
    PREMIUMPAID = 0
    PAID = 1
    FREE = 2


class TabKeys(Enum):
    SENDTOFRIEND = 'sendToFriend'
    SENDTORANDOMUSER = 'sendToRandomUser'


class FillEnvelopeViewModel(ViewModel):
    __slots__ = ('onClose', 'onSendBtnClick', 'onSelectFriend', 'gotoEnvelopesInfo', 'onTabChange', 'onCongratulationSelect', 'onDropdownClick')

    def __init__(self, properties=13, commands=7):
        super(FillEnvelopeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedFriend(self):
        return self._getViewModel(0)

    def getEnvelopeType(self):
        return EnvelopeType(self._getNumber(1))

    def setEnvelopeType(self, value):
        self._setNumber(1, value.value)

    def getCountEnvelopes(self):
        return self._getNumber(2)

    def setCountEnvelopes(self, value):
        self._setNumber(2, value)

    def getIsForRandomUser(self):
        return self._getBool(3)

    def setIsForRandomUser(self, value):
        self._setBool(3, value)

    def getIsValidFriend(self):
        return self._getBool(4)

    def setIsValidFriend(self, value):
        self._setBool(4, value)

    def getCongratulation(self):
        return self._getNumber(5)

    def setCongratulation(self, value):
        self._setNumber(5, value)

    def getFriends(self):
        return self._getArray(6)

    def setFriends(self, value):
        self._setArray(6, value)

    def getIsErrorState(self):
        return self._getBool(7)

    def setIsErrorState(self, value):
        self._setBool(7, value)

    def getSendingComplete(self):
        return self._getBool(8)

    def setSendingComplete(self, value):
        self._setBool(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    def getHasDropdownBeenClicked(self):
        return self._getBool(10)

    def setHasDropdownBeenClicked(self, value):
        self._setBool(10, value)

    def getHasCongratulationBeenClicked(self):
        return self._getBool(11)

    def setHasCongratulationBeenClicked(self, value):
        self._setBool(11, value)

    def getAccountNameMaxLength(self):
        return self._getNumber(12)

    def setAccountNameMaxLength(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(FillEnvelopeViewModel, self)._initialize()
        self._addViewModelProperty('selectedFriend', FriendModel())
        self._addNumberProperty('envelopeType')
        self._addNumberProperty('countEnvelopes', 0)
        self._addBoolProperty('isForRandomUser', False)
        self._addBoolProperty('isValidFriend', True)
        self._addNumberProperty('congratulation', 1)
        self._addArrayProperty('friends', Array())
        self._addBoolProperty('isErrorState', False)
        self._addBoolProperty('sendingComplete', False)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('hasDropdownBeenClicked', False)
        self._addBoolProperty('hasCongratulationBeenClicked', False)
        self._addNumberProperty('accountNameMaxLength', 0)
        self.onClose = self._addCommand('onClose')
        self.onSendBtnClick = self._addCommand('onSendBtnClick')
        self.onSelectFriend = self._addCommand('onSelectFriend')
        self.gotoEnvelopesInfo = self._addCommand('gotoEnvelopesInfo')
        self.onTabChange = self._addCommand('onTabChange')
        self.onCongratulationSelect = self._addCommand('onCongratulationSelect')
        self.onDropdownClick = self._addCommand('onDropdownClick')
