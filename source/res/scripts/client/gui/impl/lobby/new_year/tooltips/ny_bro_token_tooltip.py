# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_bro_token_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_bro_token_tooltip_model import NyBroTokenTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.new_year.ny_views_helpers import giftsPogressQuestFilter, giftsSubprogressQuestFilter, getGiftsTokensCountByID, getTimerGameDayLeft
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency
from helpers.time_utils import getDayTimeLeft, ONE_MINUTE
from new_year.ny_constants import NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN, NY_GIFT_SYSTEM_PROGRESSION_TOKEN
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.ny.constants import LogGroups
from uilogging.ny.loggers import NyGiftSystemViewTooltipLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class NyBroTokenTooltip(ViewImpl):
    __slots__ = ('__notifier',)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __uiLogger = NyGiftSystemViewTooltipLogger(LogGroups.BRO_ICON.value)

    def __init__(self, layoutID=R.views.lobby.new_year.tooltips.NyBroTokenTooltip()):
        super(NyBroTokenTooltip, self).__init__(ViewSettings(layoutID, model=NyBroTokenTooltipModel()))
        self.__notifier = PeriodicNotifier(getTimerGameDayLeft, self.__updateClearingTimer, (ONE_MINUTE,))

    @property
    def viewModel(self):
        return super(NyBroTokenTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyBroTokenTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            self.__updateProgression(model=model)
            self.__updateClearingTimer()
        self.__notifier.startNotification()

    def _onLoaded(self, *args, **kwargs):
        super(NyBroTokenTooltip, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onTooltipOpened()

    def _initialize(self, *args, **kwargs):
        super(NyBroTokenTooltip, self)._initialize()
        self.__eventsCache.onSyncCompleted += self.__updateProgression

    def _finalize(self):
        super(NyBroTokenTooltip, self)._finalize()
        self.__eventsCache.onSyncCompleted -= self.__updateProgression
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__uiLogger.onTooltipClosed()

    def __invalidateStages(self, requiredAmount):
        requiredAmount.clear()
        progressQuests = self.__eventsCache.getHiddenQuests(giftsPogressQuestFilter)
        for quest in sorted(progressQuests.itervalues(), key=lambda q: q.getID()):
            requiredAmount.addNumber(getGiftsTokensCountByID(quest.getID()))

        requiredAmount.invalidate()

    def __updateClearingTimer(self):
        self.viewModel.setRebootTimer(getDayTimeLeft())

    @replaceNoneKwargsModel
    def __updateProgression(self, model=None):
        subprogressQuests = self.__eventsCache.getHiddenQuests(giftsSubprogressQuestFilter)
        subprogressQuest = subprogressQuests.itervalues().next() if subprogressQuests else None
        model.setCurrentCount(self.__itemsCache.items.tokens.getTokenCount(NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN))
        model.setTotalCount(getGiftsTokensCountByID(subprogressQuest.getID()) if subprogressQuest else 0)
        model.setBroTokenCount(self.__itemsCache.items.tokens.getTokenCount(NY_GIFT_SYSTEM_PROGRESSION_TOKEN))
        self.__invalidateStages(model.getAmountRequired())
        return
