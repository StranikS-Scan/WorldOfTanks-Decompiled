# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/progression_entry_point_view.py
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.hangar_progression_view_model import HangarProgressionViewModel
from white_tiger.gui.impl.lobby.tooltips.progression_widget_tooltip_view import ProgressionWidgetTooltipView
from white_tiger.gui.shared.event_dispatcher import showProgressionScreen
from white_tiger.gui.white_tiger_account_settings import getSettings, AccountSettingsKeys
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.skeletons.economics_controller import IEconomicsController

class ProgressionEntryPointView(ViewComponent[HangarProgressionViewModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __whiteTigerCtrl = dependency.descriptor(IWhiteTigerController)
    __economicsCtrl = dependency.descriptor(IEconomicsController)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.Progression(), **kwargs):
        super(ProgressionEntryPointView, self).__init__(layoutID=layoutID, model=HangarProgressionViewModel)

    @property
    def viewModel(self):
        return super(ProgressionEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ProgressionWidgetTooltipView() if contentID == R.views.white_tiger.mono.lobby.tooltips.progression_widget_tooltip() else super(ProgressionEntryPointView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onWidgetClick), (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted), (self.__economicsCtrl.onProgressSeenByUser, self.__onProgressSeenByUser))

    @sf_lobby
    def __app(self):
        return None

    def _onLoading(self, *args, **kwargs):
        super(ProgressionEntryPointView, self)._onLoading()
        self.__fillModel()

    def __fillModel(self):
        stageFinished = self.__economicsCtrl.getFinishedLevelsCount()
        maxProgression = self.__economicsCtrl.getProgressionMaxLevel()
        isProgressionCompleted = stageFinished == maxProgression
        with self.viewModel.transaction() as vm:
            vm.setAllCollected(isProgressionCompleted)
            vm.setCurrentProgression(stageFinished)
            vm.setTotalProgression(maxProgression)
            vm.setIsNewItem(self.hasNewItems())

    def hasNewItems(self):
        currentStamps = self.__economicsCtrl.getStampsCount()
        previousSeenStamps = getSettings(AccountSettingsKeys.WT_LAST_SEEN_STAMPS)
        return currentStamps > previousSeenStamps

    def __onSyncCompleted(self, reason, diff):
        if self.__whiteTigerCtrl.isEventPrbActive():
            self.__fillModel()

    def __onWidgetClick(self):
        showProgressionScreen()

    def __onProgressSeenByUser(self, currentlySeenStamps, currentlySeenLevel):
        with self.viewModel.transaction() as vm:
            currentStamps = self.__economicsCtrl.getStampsCount()
            vm.setIsNewItem(currentlySeenStamps < currentStamps)
