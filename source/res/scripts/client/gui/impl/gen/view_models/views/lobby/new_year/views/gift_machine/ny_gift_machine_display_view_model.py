# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_machine/ny_gift_machine_display_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.gift_machine_reward_item_model import GiftMachineRewardItemModel

class NyGiftMachineDisplayViewModel(ViewModel):
    __slots__ = ('onRewardAnimationEnd',)

    def __init__(self, properties=3, commands=1):
        super(NyGiftMachineDisplayViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def reward(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardType():
        return GiftMachineRewardItemModel

    def getMachineState(self):
        return self._getString(1)

    def setMachineState(self, value):
        self._setString(1, value)

    def getTokenCount(self):
        return self._getNumber(2)

    def setTokenCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyGiftMachineDisplayViewModel, self)._initialize()
        self._addViewModelProperty('reward', GiftMachineRewardItemModel())
        self._addStringProperty('machineState', '')
        self._addNumberProperty('tokenCount', 0)
        self.onRewardAnimationEnd = self._addCommand('onRewardAnimationEnd')
