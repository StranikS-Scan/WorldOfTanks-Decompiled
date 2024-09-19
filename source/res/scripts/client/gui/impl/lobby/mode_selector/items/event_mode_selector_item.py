# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/event_mode_selector_item.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MODE_SELECTOR_BATTLE_PASS_SHOWN
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_wt_model import ModeSelectorWtModel
from gui.impl.lobby.mode_selector.items import BATTLE_PASS_SEASON_ID
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventBattlesController, IBattlePassController
_logger = logging.getLogger(__name__)

class EventModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorWtModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.WT
    __eventController = dependency.descriptor(IEventBattlesController)
    __battlePassController = dependency.descriptor(IBattlePassController)

    @property
    def viewModel(self):
        return super(EventModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(EventModeSelectorItem, self)._onInitializing()
        self.__setupBattlePassUI()
        self.__addListeners()
        self.__setData()
        self._addReward(ModeSelectorRewardID.OTHER)

    def _isInfoIconVisible(self):
        return True

    def _getDisabledTooltipText(self):
        return backport.text(R.strings.event.popover.harrierEvent.tooltip.header()) if not self.__eventController.isModeActive() else super(EventModeSelectorItem, self)._getDisabledTooltipText()

    def __setupBattlePassUI(self):
        seasonId = self.__battlePassController.getSeasonStartTime()
        bpSettings = AccountSettings.getSettings(MODE_SELECTOR_BATTLE_PASS_SHOWN)
        isShown = bpSettings.get(self.viewModel.getModeName(), False)
        isNewSeason = bpSettings.get(BATTLE_PASS_SEASON_ID, 0) != seasonId
        state = BattlePassState.STATIC if isShown and not isNewSeason else BattlePassState.NEW
        self.viewModel.setBattlePassState(state)

    def _onDisposing(self):
        self.__removeListeners()
        super(EventModeSelectorItem, self)._onDisposing()

    def __addListeners(self):
        self.__eventController.onUpdated += self.__onUpdated
        self.__eventController.onPrimeTimeStatusUpdated += self.__onUpdated
        self.__eventController.onGameEventTick += self.__onUpdated

    def __removeListeners(self):
        self.__eventController.onPrimeTimeStatusUpdated -= self.__onUpdated
        self.__eventController.onUpdated -= self.__onUpdated
        self.__eventController.onGameEventTick -= self.__onUpdated

    def __setData(self):
        with self.viewModel.transaction() as model:
            self.__fillWidget(model.widget)
            self.__updateTimeLeft(model)

    def __onUpdated(self, *_):
        self.__setData()

    def __fillWidget(self, model):
        ctrl = self.__eventController
        model.setIsEnabled(ctrl.isEnabled())
        model.setCurrentProgress(ctrl.getFinishedLevelsCount())
        model.setTotalCount(ctrl.getTotalLevelsCount())
        model.setTicketCount(ctrl.getTicketCount())

    def __updateTimeLeft(self, model):
        if self.__eventController.isModeActive():
            timeLeft = self.__getEndCycleTime()
            model.setTimeLeft(str(timeLeft))

    def __getEndCycleTime(self):
        currentSeason = self.__eventController.getCurrentSeason()
        cycleEndTime = currentSeason.getCycleEndDate()
        if cycleEndTime is None:
            _logger.error('There is not active cycle of the event battles')
            return ''
        else:
            return getFormattedTimeLeft(max(0, cycleEndTime - time_utils.getServerUTCTime()))
