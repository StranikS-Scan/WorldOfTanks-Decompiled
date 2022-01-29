# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/open_envelopes_award_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.envelope_award_view_model import EnvelopeAwardViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.reward_view_model import RewardViewModel

class EnvelopeType(IntEnum):
    PREMIUMPAID = 0
    PAID = 1
    FREE = 2


class RequestStatus(IntEnum):
    INPROGRESS = 0
    SUCCESS = 1
    ERROR = 2


class OpenEnvelopesAwardViewModel(ViewModel):
    __slots__ = ('onOpenNext', 'onGoToStorage', 'onSendEnvelope', 'onAnimationEnabled', 'onAddToFriend', 'onClickInfoLink')

    def __init__(self, properties=6, commands=6):
        super(OpenEnvelopesAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getAnimationEnabled(self):
        return self._getBool(0)

    def setAnimationEnabled(self, value):
        self._setBool(0, value)

    def getEnvelopesCount(self):
        return self._getNumber(1)

    def setEnvelopesCount(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getEnvelopes(self):
        return self._getArray(3)

    def setEnvelopes(self, value):
        self._setArray(3, value)

    def getEnvelopesType(self):
        return EnvelopeType(self._getNumber(4))

    def setEnvelopesType(self, value):
        self._setNumber(4, value.value)

    def getOpenEnvelopesRequestStatus(self):
        return RequestStatus(self._getNumber(5))

    def setOpenEnvelopesRequestStatus(self, value):
        self._setNumber(5, value.value)

    def _initialize(self):
        super(OpenEnvelopesAwardViewModel, self)._initialize()
        self._addBoolProperty('animationEnabled', True)
        self._addNumberProperty('envelopesCount', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('envelopes', Array())
        self._addNumberProperty('envelopesType')
        self._addNumberProperty('openEnvelopesRequestStatus')
        self.onOpenNext = self._addCommand('onOpenNext')
        self.onGoToStorage = self._addCommand('onGoToStorage')
        self.onSendEnvelope = self._addCommand('onSendEnvelope')
        self.onAnimationEnabled = self._addCommand('onAnimationEnabled')
        self.onAddToFriend = self._addCommand('onAddToFriend')
        self.onClickInfoLink = self._addCommand('onClickInfoLink')
