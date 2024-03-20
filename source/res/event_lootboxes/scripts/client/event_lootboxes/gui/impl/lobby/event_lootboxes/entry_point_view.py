# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/entry_point_view.py
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from event_lootboxes.gui.shared.event_dispatcher import showEventLootBoxesWelcomeScreen
from gui.impl.gen import R
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.entry_point_view_model import EntryPointViewModel
from tooltips.entry_point_tooltip import EventLootBoxesEntryPointTooltipView
from popover import EventLootBoxesPopover
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY
from helpers import dependency
from helpers.time_utils import ONE_DAY, getServerUTCTime
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.hangar import ICarouselEventEntry
_ENABLED_PRE_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.WINBACK, QUEUE_TYPE.BATTLE_ROYALE)

class EventLootBoxesEntryPointWidget(ViewImpl, ICarouselEventEntry):
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)

    def __init__(self):
        super(EventLootBoxesEntryPointWidget, self).__init__(ViewSettings(R.views.event_lootboxes.lobby.event_lootboxes.EntryPointView(), ViewFlags.VIEW, EntryPointViewModel()))

    @property
    def viewModel(self):
        return super(EventLootBoxesEntryPointWidget, self).getViewModel()

    @staticmethod
    def getIsActive(state):
        return EventLootBoxesEntryPointWidget.__eventLootBoxes.isActive() and (any((state.isInPreQueue(preQueue) for preQueue in _ENABLED_PRE_QUEUES)) or state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE))

    def createPopOverContent(self, event):
        return EventLootBoxesPopover()

    def createToolTipContent(self, event, contentID):
        return EventLootBoxesEntryPointTooltipView() if contentID == R.views.event_lootboxes.lobby.event_lootboxes.tooltips.EntryPointTooltip() else None

    def _initialize(self, *args, **kwargs):
        self.__showWelcomeIfNeeded()

    def _onLoading(self, *args, **kwargs):
        super(EventLootBoxesEntryPointWidget, self)._onLoading(*args, **kwargs)
        self.__updateBoxesCount(self.__eventLootBoxes.getBoxesCount())
        self.__updateTime()

    def _getEvents(self):
        return ((self.__eventLootBoxes.onBoxesCountChange, self.__updateBoxesCount), (self.__eventLootBoxes.onStatusChange, self.__onLootBoxesStatusChanged), (self.viewModel.onWidgetClick, self.__onWidgetClick))

    def __onWidgetClick(self):
        self.viewModel.setHasNew(False)
        self.__eventLootBoxes.setSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_VIEWED_COUNT, self.__eventLootBoxes.getBoxesCount())

    def __onLootBoxesStatusChanged(self):
        self.__showWelcomeIfNeeded()
        self.__updateTime()

    def __updateBoxesCount(self, count, *_):
        lastViewed = self.__eventLootBoxes.getSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_VIEWED_COUNT)
        with self.viewModel.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)

    def __getTimeToTimerUpdate(self):
        return max(self.__getEventExpireTime() - ONE_DAY, 0)

    def __updateTime(self):
        self.viewModel.setEventExpireTime(self.__getEventExpireTime())

    def __getEventExpireTime(self):
        _, finish = self.__eventLootBoxes.getEventActiveTime()
        return finish - getServerUTCTime()

    def __showWelcomeIfNeeded(self):
        if not self.__eventLootBoxes.isLootBoxesWasStarted():
            showEventLootBoxesWelcomeScreen()
