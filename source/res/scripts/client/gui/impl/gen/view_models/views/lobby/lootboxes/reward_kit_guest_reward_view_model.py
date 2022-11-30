# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/reward_kit_guest_reward_view_model.py
from frameworks.wulf import ViewModel

class RewardKitGuestRewardViewModel(ViewModel):
    __slots__ = ('onContinue', 'onGoQuests', 'onClose', 'onVideoStarted', 'onVideoStopped')

    def __init__(self, properties=3, commands=5):
        super(RewardKitGuestRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getStreamBufferLength(self):
        return self._getNumber(0)

    def setStreamBufferLength(self, value):
        self._setNumber(0, value)

    def getIsViewAccessible(self):
        return self._getBool(1)

    def setIsViewAccessible(self, value):
        self._setBool(1, value)

    def getRealm(self):
        return self._getString(2)

    def setRealm(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(RewardKitGuestRewardViewModel, self)._initialize()
        self._addNumberProperty('streamBufferLength', 1)
        self._addBoolProperty('isViewAccessible', True)
        self._addStringProperty('realm', '')
        self.onContinue = self._addCommand('onContinue')
        self.onGoQuests = self._addCommand('onGoQuests')
        self.onClose = self._addCommand('onClose')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
