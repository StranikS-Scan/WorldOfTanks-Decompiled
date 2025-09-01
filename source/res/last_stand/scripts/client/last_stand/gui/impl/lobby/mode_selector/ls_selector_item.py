# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/mode_selector/ls_selector_item.py
import typing
from account_helpers.AccountSettings import MODE_SELECTOR_BATTLE_PASS_SHOWN, AccountSettings
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_performance_model import PerformanceRiskEnum
from gui.impl.lobby.mode_selector.items import resetBattlePassStateForItem, BATTLE_PASS_SEASON_ID
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.event_dispatcher import showBrowserOverlayView
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings
from last_stand.gui.ls_gui_constants import VIEW_ALIAS, LS_INFO_PAGE_KEY
from last_stand.gui.shared.utils.performance_analyzer import PerformanceGroup
from helpers import dependency, time_utils
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, getFormattedTimeLeft
from last_stand.skeletons.ls_controller import ILSController
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class LSSelectorItem(ModeSelectorLegacyItem):
    lsCtrl = dependency.descriptor(ILSController)
    bpController = dependency.descriptor(IBattlePassController)

    def _onInitializing(self):
        super(LSSelectorItem, self)._onInitializing()
        self.lsCtrl.onSettingsUpdate += self.__onEventUpdate
        for reward in self.lsCtrl.getModeSettings().modeSelectorShowRewards.get('rewards', []):
            value = getattr(ModeSelectorRewardID, reward, None)
            if value is not None:
                self._addReward(value)

        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getEndDate())
            vm.performance.setShowPerfRisk(True)
            vm.performance.setPerformanceRisk(PERFORMANCE_MAP.get(self.lsCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            vm.setIsNew(getSettings(AccountSettingsKeys.IS_EVENT_NEW))
            vm.setIsSelected(self.lsCtrl.isEventPrb())
            self.__setBattlePassState(vm)
        return

    @property
    def isSelectable(self):
        return False

    @property
    def calendarTooltipText(self):
        endDate = self.lsCtrl.getModeSettings().endDate
        timeValue = max(0, endDate - time_utils.getServerUTCTime())
        return backport.text(R.strings.mode_selector.mode.last_stand.calendar(), date=self.__getEndDate()) if timeValue >= time_utils.ONE_DAY else backport.text(R.strings.mode_selector.mode.last_stand.calendarDay(), date=self.__getEndDate())

    def handleClick(self):
        if self.lsCtrl.isEventPrb():
            return
        self.lsCtrl.selectBattle()

    def handleInfoPageClick(self):
        url = self._urlProcessing(GUI_SETTINGS.lookup(LS_INFO_PAGE_KEY))
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _isInfoIconVisible(self):
        return GUI_SETTINGS.lookup(LS_INFO_PAGE_KEY) is not None

    def _onDisposing(self):
        self.lsCtrl.onSettingsUpdate -= self.__onEventUpdate
        super(LSSelectorItem, self)._onDisposing()

    def __onEventUpdate(self, *_):
        self.onCardChange()

    def __getEndDate(self):
        endDate = self.lsCtrl.getModeSettings().endDate
        return getFormattedTimeLeft(max(0, endDate - time_utils.getServerUTCTime()))

    def __setBattlePassState(self, itemVM):
        isActive = self.bpController.isEnabled()
        isPaused = self.bpController.isPaused()
        isOffSeason = not self.bpController.isSeasonStarted() or self.bpController.isSeasonFinished()
        hasStatusNotActive = bool(itemVM.getStatusNotActive())
        seasonId = self.bpController.getSeasonStartTime()
        isShown = self.lsCtrl.getModeSettings().modeSelectorShowRewards.get('battlePassPoints', False)
        if not isShown or not isActive or isPaused or isOffSeason or hasStatusNotActive:
            resetBattlePassStateForItem(itemVM)
            return
        bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
        isShown = bpSettings.get(itemVM.getModeName(), False)
        isNewSeason = bpSettings.get(BATTLE_PASS_SEASON_ID, 0) != seasonId
        state = BattlePassState.STATIC if isShown and not isNewSeason else BattlePassState.NEW
        itemVM.setBattlePassState(state)
