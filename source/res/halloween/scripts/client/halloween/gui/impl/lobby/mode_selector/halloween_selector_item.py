# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/mode_selector/halloween_selector_item.py
from __future__ import absolute_import
import typing
from account_helpers.AccountSettings import MODE_SELECTOR_BATTLE_PASS_SHOWN, AccountSettings
from helpers.time_utils import ONE_DAY
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.mode_performance_model import PerformanceRiskEnum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.lobby.mode_selector.items import resetBattlePassStateForItem, BATTLE_PASS_SEASON_ID
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, getFormattedTimeLeft
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from halloween.gui.halloween_account_settings import AccountSettingsKeys, getSettings
from halloween.gui.shared.event_dispatcher import showInfoPage
from halloween.gui.shared.utils.performance_analyzer import PerformanceGroup
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency, time_utils, int2roman
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class HalloweenSelectorItem(ModeSelectorLegacyItem):
    __hwBattleCtrl = dependency.descriptor(IHalloweenController)
    __hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    __bpController = dependency.descriptor(IBattlePassController)

    def _onInitializing(self):
        super(HalloweenSelectorItem, self)._onInitializing()
        self.__hwBattleCtrl.onSettingsUpdate += self.__onHalloweenUpdate
        self.__uiLogger = HWMetricsLogger(HWLogKeys.MODE_SELECTOR_VIEW)
        for reward in self.__hwBattleCtrl.getModeSettings().modeSelectorShowRewards.get('rewards', []):
            value = getattr(ModeSelectorRewardID, reward, None)
            if value is None:
                continue
            if value == ModeSelectorRewardID.VEHICLE:
                vehicle = self.__hwArtefactsCtrl.getMainGiftVehicle()
                if vehicle:
                    self._addReward(ModeSelectorRewardID.VEHICLE, locParams={'name': vehicle.userName}, level=int2roman(vehicle.level), type=vehicle.type, isPremium=vehicle.isPremium)
            self._addReward(value)

        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getEndDate())
            vm.performance.setShowPerfRisk(True)
            vm.performance.setPerformanceRisk(PERFORMANCE_MAP.get(self.__hwBattleCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            vm.setIsNew(getSettings(AccountSettingsKeys.IS_EVENT_NEW))
            vm.setIsSelected(self.__hwBattleCtrl.isEventPrb())
            self.__setBattlePassState(vm)
        return

    @property
    def isSelectable(self):
        return False

    @property
    def calendarTooltipText(self):
        endDate = self.__hwBattleCtrl.getModeSettings().endDate
        timeValue = max(0, endDate - time_utils.getServerUTCTime())
        return backport.text(R.strings.mode_selector.mode.halloween.calendar(), date=self.__getEndDate()) if timeValue >= ONE_DAY else backport.text(R.strings.mode_selector.mode.halloween.calendarDay(), date=self.__getEndDate())

    def handleClick(self):
        if self.__hwBattleCtrl.isEventPrb():
            return
        self.__hwBattleCtrl.selectBattle(source=HWLogKeys.MODE_SELECTOR)

    def handleInfoPageClick(self):
        if not self.__hwBattleCtrl.isInfoPageEnabled():
            return
        self.__uiLogger.onClick(HWLogKeys.INFO_BUTTON)
        showInfoPage()

    def _onDisposing(self):
        self.__hwBattleCtrl.onSettingsUpdate -= self.__onHalloweenUpdate
        super(HalloweenSelectorItem, self)._onDisposing()

    def _isInfoIconVisible(self):
        return self.__hwBattleCtrl.isInfoPageEnabled() and super(HalloweenSelectorItem, self)._isInfoIconVisible()

    def __onHalloweenUpdate(self, *_):
        self.onCardChange()

    def __getEndDate(self):
        endDate = self.__hwBattleCtrl.getModeSettings().endDate
        return getFormattedTimeLeft(max(0, endDate - time_utils.getServerUTCTime()))

    def __setBattlePassState(self, itemVM):
        isActive = self.__bpController.isEnabled()
        isPaused = self.__bpController.isPaused()
        isOffSeason = not self.__bpController.isSeasonStarted() or self.__bpController.isSeasonFinished()
        hasStatusNotActive = bool(itemVM.getStatusNotActive())
        seasonId = self.__bpController.getSeasonStartTime()
        isShown = self.__hwBattleCtrl.getModeSettings().modeSelectorShowRewards.get('battlePassPoints', False)
        if not isShown or not isActive or isPaused or isOffSeason or hasStatusNotActive:
            resetBattlePassStateForItem(itemVM)
            return
        bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
        isShown = bpSettings.get(itemVM.getModeName(), False)
        isNewSeason = bpSettings.get(BATTLE_PASS_SEASON_ID, 0) != seasonId
        state = BattlePassState.STATIC if isShown and not isNewSeason else BattlePassState.NEW
        itemVM.setBattlePassState(state)
