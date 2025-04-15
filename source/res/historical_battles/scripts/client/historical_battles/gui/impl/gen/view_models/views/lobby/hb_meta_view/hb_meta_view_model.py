# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/hb_meta_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_view_model import DivisionViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.order_view_model import OrderViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.progression_view_model import ProgressionViewModel

class TabId(IntEnum):
    PROGRESS = 0
    DIVISION = 1
    ORDER = 2


class HbMetaViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onTabChange')

    def __init__(self, properties=4, commands=3):
        super(HbMetaViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressionModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionModelType():
        return ProgressionViewModel

    @property
    def divisionModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getDivisionModelType():
        return DivisionViewModel

    @property
    def orderModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getOrderModelType():
        return OrderViewModel

    def getTabId(self):
        return TabId(self._getNumber(3))

    def setTabId(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(HbMetaViewModel, self)._initialize()
        self._addViewModelProperty('progressionModel', ProgressionViewModel())
        self._addViewModelProperty('divisionModel', DivisionViewModel())
        self._addViewModelProperty('orderModel', OrderViewModel())
        self._addNumberProperty('tabId')
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onTabChange = self._addCommand('onTabChange')
