# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/need_repair_model.py
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.need_repair_content import NeedRepairContent

class NeedRepairModel(DialogWithExchange):
    __slots__ = ()

    def __init__(self, properties=17, commands=3):
        super(NeedRepairModel, self).__init__(properties=properties, commands=commands)

    @property
    def dealPanel(self):
        return self._getViewModel(15)

    @property
    def needRepairContent(self):
        return self._getViewModel(16)

    def _initialize(self):
        super(NeedRepairModel, self)._initialize()
        self._addViewModelProperty('dealPanel', DealPanelModel())
        self._addViewModelProperty('needRepairContent', NeedRepairContent())
