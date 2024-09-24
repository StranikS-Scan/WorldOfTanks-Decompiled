# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/main_overlay_model.py
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.footer_view_model import FooterViewModel

class MainOverlayModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onShowInfo')

    def __init__(self, properties=1, commands=2):
        super(MainOverlayModel, self).__init__(properties=properties, commands=commands)

    @property
    def footer(self):
        return self._getViewModel(0)

    @staticmethod
    def getFooterType():
        return FooterViewModel

    def _initialize(self):
        super(MainOverlayModel, self)._initialize()
        self._addViewModelProperty('footer', FooterViewModel())
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onShowInfo = self._addCommand('onShowInfo')
