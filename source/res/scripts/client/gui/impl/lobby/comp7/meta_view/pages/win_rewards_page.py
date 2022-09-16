# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/win_rewards_page.py
import logging
from collections import namedtuple
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_WIN_REWARDS_PAGE_WINS_COUNT
from comp7_common import Comp7QuestType
from frameworks.wulf.view.array import fillIntsArray
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.win_rewards_model import WinRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.comp7.comp7_bonus_packer import packWinsRewardsQuestBonuses
from gui.impl.lobby.comp7.comp7_quest_helpers import isComp7Quest, getComp7QuestType, parseComp7WinsQuestID
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.comp7_lobby_sounds import MetaViewSounds
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.server_events.event_items import Quest
    from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
_logger = logging.getLogger(__name__)
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class WinRewardsPage(PageSubModelPresenter):
    __slots__ = ('__quests', '__bonusData')
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, viewModel, parentView):
        super(WinRewardsPage, self).__init__(viewModel, parentView)
        self.__quests = {}
        self.__bonusData = []

    @property
    def pageId(self):
        return MetaRootViews.WINREWARDS

    @property
    def viewModel(self):
        return super(WinRewardsPage, self).getViewModel()

    @property
    def __winsCount(self):
        if not self.__quests:
            _logger.error('Failed to get current wins count. Quests are missing.')
            return 0
        else:
            finalQuest = self.__quests[max(self.__quests.iterkeys())]
            progress = finalQuest.getProgressData() or {}
            winsCount = progress.get(None, {}).get('battlesCount', 0)
            return winsCount

    def initialize(self):
        super(WinRewardsPage, self).initialize()
        self.__quests = self.__getComp7WinsQuests()
        with self.viewModel.transaction() as tx:
            self.__updateData(tx)

    def finalize(self):
        self.__quests.clear()
        self.__bonusData = []
        if self.parentView.soundManager.isSoundPlaying(MetaViewSounds.REWARD_PROGRESSBAR_START.value):
            self.parentView.soundManager.playSound(MetaViewSounds.REWARD_PROGRESSBAR_STOP.value)
        super(WinRewardsPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            bonusData = self.__bonusData[int(tooltipId)]
            window = backport.BackportTooltipWindow(bonusData.tooltip, self.parentView.getParentWindow())
            window.load()
            return window
        else:
            return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showCount'))
            bonuses = [ d.bonus for d in self.__bonusData[showCount:] ]
            return AdditionalRewardsTooltip(bonuses)
        else:
            return None

    def _getEvents(self):
        return ((self.viewModel.onSetActiveProgressPoint, self.__onSetActiveProgressPoint),
         (self.viewModel.onAnimationStart, self.__onAnimationStart),
         (self.viewModel.onAnimationEnd, self.__onAnimationEnd),
         (self.__eventsCache.onSyncCompleted, self.__onEventsSyncCompleted))

    def __updateData(self, model):
        activePoint = self.__updateProgression(model)
        self.__updateRewards(model, activePoint=activePoint)
        self.__updateWinsCount(model)

    def __updateProgression(self, model):
        currentWinsCount = self.__winsCount
        winsCounts = list(self.__quests.iterkeys())
        winsCounts.sort()
        fillIntsArray(winsCounts, model.getProgressPoints())
        if not winsCounts:
            _logger.warning('Empty Competitive7x7 Wins Quests.')
            winsCounts = [0]
        progressPoint = findFirst(lambda wc: wc > currentWinsCount, winsCounts, default=winsCounts[-1])
        if progressPoint > currentWinsCount:
            model.setNextProgressPoint(progressPoint)
        return progressPoint

    def __updateWinsCount(self, model):
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        lastWinsCount = settings.get(COMP7_WIN_REWARDS_PAGE_WINS_COUNT, 0)
        finalQuestWinsCount = max(self.__quests.iterkeys())
        finalQuest = self.__quests[finalQuestWinsCount]
        finalQuestCompleted = finalQuest.isCompleted()
        model.setIsCurrentValueLimitExceeded(finalQuestCompleted)
        currentWinsCount = finalQuestWinsCount if finalQuestCompleted else self.__winsCount
        model.setPreviousValue(lastWinsCount)
        model.setCurrentValue(currentWinsCount)
        settings[COMP7_WIN_REWARDS_PAGE_WINS_COUNT] = currentWinsCount
        AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)

    def __updateRewards(self, model, activePoint):
        model.setActiveProgressPoint(activePoint)
        quest = self.__quests.get(activePoint)
        if quest is not None:
            packedBonuses, tooltipsData = packWinsRewardsQuestBonuses(quest)
        else:
            _logger.error('Missing Competitive7x7 Wins Quest (winsCount=%s).', activePoint)
            packedBonuses, tooltipsData = (), ()
        rewards = model.getRewards()
        rewards.clear()
        self.__bonusData = []
        for idx, (packedBonus, tooltipData) in enumerate(zip(packedBonuses, tooltipsData)):
            tooltipId = str(idx)
            packedBonus.setTooltipId(tooltipId)
            rewards.addViewModel(packedBonus)
            self.__bonusData.append(_BonusData(packedBonus, tooltipData))

        rewards.invalidate()
        return

    @args2params(int)
    def __onSetActiveProgressPoint(self, activePoint):
        with self.viewModel.transaction() as tx:
            self.__updateRewards(tx, activePoint=activePoint)

    def __onAnimationStart(self):
        self.parentView.soundManager.playSound(MetaViewSounds.REWARD_PROGRESSBAR_START.value)

    def __onAnimationEnd(self):
        self.parentView.soundManager.playSound(MetaViewSounds.REWARD_PROGRESSBAR_STOP.value)

    def __onEventsSyncCompleted(self):
        self.__quests = self.__getComp7WinsQuests()
        with self.viewModel.transaction() as tx:
            self.__updateData(tx)

    @classmethod
    def __getComp7WinsQuests(cls):
        quests = cls.__eventsCache.getAllQuests(lambda q: isComp7Quest(q.getID()) and getComp7QuestType(q.getID()) == Comp7QuestType.WINS)
        quests = {parseComp7WinsQuestID(qID):quest for qID, quest in quests.iteritems()}
        return quests
