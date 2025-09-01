# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/mode_selector/white_tiger_selector_item.py
import typing
from account_helpers.AccountSettings import MODE_SELECTOR_BATTLE_PASS_SHOWN, AccountSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.hangar_progression_tooltip_view_model import PerformanceRisk
from gui.impl.lobby.mode_selector.items import resetBattlePassStateForItem, BATTLE_PASS_SEASON_ID
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.utils import SelectorBattleTypesUtils
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME
from helpers import dependency, time_utils
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, getFormattedTimeLeft
from helpers.time_utils import ONE_DAY
from skeletons.gui.game_control import IBattlePassController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_model import ModeSelectorModel
from white_tiger.skeletons.economics_controller import IEconomicsController
from gui import GUI_SETTINGS
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from frameworks.wulf import WindowLayer
if typing.TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_widget_model import ModeSelectorWidgetModel

class WhiteTigerSelectorItem(ModeSelectorLegacyItem):
    __bpController = dependency.descriptor(IBattlePassController)
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    _VIEW_MODEL = ModeSelectorModel

    @property
    def viewModel(self):
        return super(WhiteTigerSelectorItem, self).viewModel

    def _onInitializing(self):
        super(WhiteTigerSelectorItem, self)._onInitializing()
        self._addReward(ModeSelectorRewardID.OTHER)
        self.__setData()
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getEndDate())
            vm.performance.setShowPerfRisk(True)
            vm.performance.setPerformanceRisk(PerformanceRisk(self.__wtCtrl.analyzeClientSystem()))
            vm.setIsNew(not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.WHITE_TIGER))
            vm.setIsSelected(self.__wtCtrl.isEventPrbActive())
            self.__setBattlePassState(vm)

    @property
    def isSelectable(self):
        return False

    @property
    def calendarTooltipText(self):
        endDate = self.__getEndDate()
        timeValue = max(0, self.__wtCtrl.getEndDate() - time_utils.getServerUTCTime())
        return backport.text(R.strings.mode_selector.mode.whiteTiger.calendar(), date=endDate) if timeValue >= ONE_DAY else backport.text(R.strings.mode_selector.mode.whiteTiger.calendarDay(), date=endDate)

    def handleClick(self):
        self.__wtCtrl.selectBattle()

    def __getEndDate(self):
        date = self.__wtCtrl.getEndDate()
        return getFormattedTimeLeft(max(0, date - time_utils.getServerUTCTime()))

    def __setBattlePassState(self, itemVM):
        isActive = self.__bpController.isEnabled()
        isPaused = self.__bpController.isPaused()
        isOffSeason = not self.__bpController.isSeasonStarted() or self.__bpController.isSeasonFinished()
        hasStatusNotActive = bool(itemVM.getStatusNotActive())
        seasonId = self.__bpController.getSeasonStartTime()
        if not isActive or isPaused or isOffSeason or hasStatusNotActive:
            resetBattlePassStateForItem(itemVM)
            return
        bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
        isShown = bpSettings.get(itemVM.getModeName(), False)
        isNewSeason = bpSettings.get(BATTLE_PASS_SEASON_ID, 0) != seasonId
        state = BattlePassState.STATIC if isShown and not isNewSeason else BattlePassState.NEW
        itemVM.setBattlePassState(state)

    def __setData(self):
        self.__fillViewModel()
        self.__fillWidget()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setExternalPath(R.views.white_tiger.lobby.BattleCard())

    def __fillWidget(self):
        with self.viewModel.widget.transaction() as vm:
            ctrl = self.__wtCtrl
            vm.setIsEnabled(ctrl.isEnabled())
            vm.setCurrentProgress(self.__economicsCtrl.getFinishedLevelsCount())
            vm.setTotalCount(self.__economicsCtrl.getProgressionMaxLevel())
            vm.setTicketCount(self.__economicsCtrl.getTicketCount())

    def _isInfoIconVisible(self):
        return True

    def handleInfoPageClick(self):
        url = GUI_SETTINGS.lookup('wtEventInfoPage')
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
