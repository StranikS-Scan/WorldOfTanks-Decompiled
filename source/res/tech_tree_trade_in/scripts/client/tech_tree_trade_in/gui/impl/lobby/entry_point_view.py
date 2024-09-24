# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/entry_point_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from helpers import dependency, time_utils
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.entry_point_view_model import EntryPointViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from tech_tree_trade_in.gui.impl.lobby.tooltips.widget_tooltip_view import WidgetTooltipView
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController

def getTimestampDelta(timestamp):
    return timestamp - time_utils.getCurrentLocalServerTimestamp()


class EntryPointView(ViewImpl):
    __slots__ = ('__isExtended',)
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)

    def __init__(self, isExtended=False):
        settings = ViewSettings(R.views.tech_tree_trade_in.lobby.EntryPointView())
        settings.flags = ViewFlags.VIEW
        settings.model = EntryPointViewModel()
        self.__isExtended = isExtended
        super(EntryPointView, self).__init__(settings)

    def _finalize(self):
        self.__techTreeTradeInController.onSettingsChanged -= self.__onUpdate
        self.__techTreeTradeInController.onEntryPointUpdated -= self.__onUpdate
        self.__techTreeTradeInController.onPlayerTradeInStatusChanged -= self.__onUpdate
        super(EntryPointView, self)._finalize()

    def _initialize(self, *args, **kwargs):
        super(EntryPointView, self)._initialize(*args, **kwargs)
        self.__techTreeTradeInController.onSettingsChanged += self.__onUpdate
        self.__techTreeTradeInController.onEntryPointUpdated += self.__onUpdate
        self.__techTreeTradeInController.onPlayerTradeInStatusChanged += self.__onUpdate

    def __onUpdate(self, *_):
        self.__updateViewModel()

    @property
    def viewModel(self):
        return super(EntryPointView, self).getViewModel()

    def setIsExtended(self, value):
        self.__isExtended = value
        self.__updateViewModel()

    def __getEndTime(self):
        return getTimestampDelta(self.__techTreeTradeInController.getEndTime())

    def createToolTipContent(self, event, contentID):
        return WidgetTooltipView(self.__getEndTime()) if contentID == R.views.tech_tree_trade_in.lobby.tooltips.WidgetTooltipView() else super(EntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(EntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick),)

    def __onClick(self):
        self.__techTreeTradeInController.showTechTreeTradeInView()

    def __updateViewModel(self):
        if self.__techTreeTradeInController.isTechTreeTradeInEntryPointEnabled:
            with self.viewModel.transaction() as tx:
                if tx is None:
                    return
                tx.setDateEnd(self.__getEndTime())
                tx.setIsExtended(self.__isExtended)
        return
