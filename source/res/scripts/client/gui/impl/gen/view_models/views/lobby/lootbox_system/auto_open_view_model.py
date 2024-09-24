# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/auto_open_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.reward_row_model import RewardRowModel

class AutoOpenViewModel(ViewModel):
    __slots__ = ('onClose', 'onPreview')

    def __init__(self, properties=3, commands=2):
        super(AutoOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getBoxesQuantity(self):
        return self._getNumber(1)

    def setBoxesQuantity(self, value):
        self._setNumber(1, value)

    def getRewardRows(self):
        return self._getArray(2)

    def setRewardRows(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardRowsType():
        return RewardRowModel

    def _initialize(self):
        super(AutoOpenViewModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addNumberProperty('boxesQuantity', 0)
        self._addArrayProperty('rewardRows', Array())
        self.onClose = self._addCommand('onClose')
        self.onPreview = self._addCommand('onPreview')
