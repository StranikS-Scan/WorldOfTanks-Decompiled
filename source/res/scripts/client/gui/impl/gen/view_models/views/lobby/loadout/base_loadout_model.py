# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/base_loadout_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel

class BaseLoadoutModel(ViewModel):
    __slots__ = ('onSlotAction',)

    def __init__(self, properties=1, commands=1):
        super(BaseLoadoutModel, self).__init__(properties=properties, commands=commands)

    @property
    def dealPanel(self):
        return self._getViewModel(0)

    @staticmethod
    def getDealPanelType():
        return DealPanelModel

    def _initialize(self):
        super(BaseLoadoutModel, self)._initialize()
        self._addViewModelProperty('dealPanel', DealPanelModel())
        self.onSlotAction = self._addCommand('onSlotAction')
