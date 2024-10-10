# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/mode_selector/white_tiger_mode_selector_item.py
import logging
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.game_control.wt_controller import WtPerfProblems
from gui.wt_event.wt_event_helpers import getSecondsLeft
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.wt_event.wt_event_helpers import getInfoPageURL
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_wt_model import ModeSelectorWtModel, PerformanceRisk
PERFORMANCE_MAP = {WtPerfProblems.LOW_RISK: PerformanceRisk.LOW,
 WtPerfProblems.MEDIUM_RISK: PerformanceRisk.MEDIUM,
 WtPerfProblems.HIGH_RISK: PerformanceRisk.HIGH}
_logger = logging.getLogger(__name__)

class WhiteTigerModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorWtModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.WT
    __wtController = dependency.descriptor(IWhiteTigerController)

    @property
    def viewModel(self):
        return super(WhiteTigerModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(WhiteTigerModeSelectorItem, self)._onInitializing()
        self.viewModel.setBattlePassState(BattlePassState.STATIC)
        self.__addListeners()
        self.__setData()
        self._addReward(ModeSelectorRewardID.WT_2024_CREW)
        self._addReward(ModeSelectorRewardID.BONES)
        self._addReward(ModeSelectorRewardID.WT_2024_OTHER)

    def _onDisposing(self):
        self.__removeListeners()
        super(WhiteTigerModeSelectorItem, self)._onDisposing()

    def _getIsDisabled(self):
        return self.__wtController.isFrozen()

    def __addListeners(self):
        self.__wtController.onUpdated += self.__onUpdated
        self.__wtController.onPrimeTimeStatusUpdated += self.__onUpdated
        self.__wtController.onGameEventTick += self.__onUpdated

    def __removeListeners(self):
        self.__wtController.onPrimeTimeStatusUpdated -= self.__onUpdated
        self.__wtController.onUpdated -= self.__onUpdated
        self.__wtController.onGameEventTick -= self.__onUpdated

    def __setData(self):
        with self.viewModel.transaction() as model:
            self.__fillWidget(model.widget)
            self.__updateTimeLeft(model)
            model.setPerformanceRisk(PERFORMANCE_MAP.get(self.__wtController.analyzeClientSystem(), PerformanceRisk.LOW))

    def __onUpdated(self, *_):
        self.__setData()

    def __fillWidget(self, model):
        ctrl = self.__wtController
        model.setIsEnabled(ctrl.isEnabled())
        model.setCurrentProgress(ctrl.getFinishedLevelsCount())
        model.setTotalCount(ctrl.getTotalLevelsCount())
        model.setTicketCount(ctrl.getTicketCount())

    def __updateTimeLeft(self, model):
        if self.__wtController.isModeActive():
            timeLeft = self.__getEndTime()
            model.setTimeLeft(str(timeLeft))

    def __getEndTime(self):
        return getFormattedTimeLeft(getSecondsLeft())

    def handleInfoPageClick(self):
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def _isInfoIconVisible(self):
        return getInfoPageURL() is not None
