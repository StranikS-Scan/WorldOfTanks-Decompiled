# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/event_mode_selector_item.py
import logging
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_wt_model import ModeSelectorWtModel
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)

class EventModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorWtModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.WT
    __eventController = dependency.descriptor(IEventBattlesController)

    @property
    def viewModel(self):
        return super(EventModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(EventModeSelectorItem, self)._onInitializing()
        setBattlePassState(self.viewModel)
        self.__addListeners()
        self.__setData()
        self._addReward(ModeSelectorRewardID.OTHER)

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
