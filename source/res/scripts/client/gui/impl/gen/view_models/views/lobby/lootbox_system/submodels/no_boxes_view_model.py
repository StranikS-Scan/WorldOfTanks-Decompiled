# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/no_boxes_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_info_model import BoxInfoModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.statistics_model import StatisticsModel

class NoBoxesViewModel(ViewModel):
    __slots__ = ('onInfoOpen', 'onBuyBoxes', 'onClose')

    def __init__(self, properties=5, commands=3):
        super(NoBoxesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def statistics(self):
        return self._getViewModel(0)

    @staticmethod
    def getStatisticsType():
        return StatisticsModel

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def getBoxesInfo(self):
        return self._getArray(2)

    def setBoxesInfo(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBoxesInfoType():
        return BoxInfoModel

    def getUseExternal(self):
        return self._getBool(3)

    def setUseExternal(self, value):
        self._setBool(3, value)

    def getUseStats(self):
        return self._getBool(4)

    def setUseStats(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NoBoxesViewModel, self)._initialize()
        self._addViewModelProperty('statistics', StatisticsModel())
        self._addStringProperty('eventName', '')
        self._addArrayProperty('boxesInfo', Array())
        self._addBoolProperty('useExternal', False)
        self._addBoolProperty('useStats', True)
        self.onInfoOpen = self._addCommand('onInfoOpen')
        self.onBuyBoxes = self._addCommand('onBuyBoxes')
        self.onClose = self._addCommand('onClose')
