# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/tech_tree_trade_in_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_selection_view_model import BranchSelectionViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.intro_view_model import IntroViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.main_overlay_model import MainOverlayModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.multicurrency_selection_view_model import MulticurrencySelectionViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.post_trade_view_model import PostTradeViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.summary_view_model import SummaryViewModel

class MainViews(IntEnum):
    INTRO = 0
    BRANCH_SELECTION = 1
    SUMMARY = 2
    MULTICURRENCY_SELECTION = 3
    POST_TRADE = 4


class TechTreeTradeInViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=7, commands=1):
        super(TechTreeTradeInViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainOverlayModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainOverlayModelType():
        return MainOverlayModel

    @property
    def introModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getIntroModelType():
        return IntroViewModel

    @property
    def branchSelectionModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getBranchSelectionModelType():
        return BranchSelectionViewModel

    @property
    def summaryModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getSummaryModelType():
        return SummaryViewModel

    @property
    def postTradeModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getPostTradeModelType():
        return PostTradeViewModel

    @property
    def multicurrencySelectionModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getMulticurrencySelectionModelType():
        return MulticurrencySelectionViewModel

    def getViewType(self):
        return MainViews(self._getNumber(6))

    def setViewType(self, value):
        self._setNumber(6, value.value)

    def _initialize(self):
        super(TechTreeTradeInViewModel, self)._initialize()
        self._addViewModelProperty('mainOverlayModel', MainOverlayModel())
        self._addViewModelProperty('introModel', IntroViewModel())
        self._addViewModelProperty('branchSelectionModel', BranchSelectionViewModel())
        self._addViewModelProperty('summaryModel', SummaryViewModel())
        self._addViewModelProperty('postTradeModel', PostTradeViewModel())
        self._addViewModelProperty('multicurrencySelectionModel', MulticurrencySelectionViewModel())
        self._addNumberProperty('viewType')
        self.onClose = self._addCommand('onClose')
