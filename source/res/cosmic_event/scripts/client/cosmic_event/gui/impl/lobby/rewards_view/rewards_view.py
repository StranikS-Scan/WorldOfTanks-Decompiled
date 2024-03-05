# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/rewards_view/rewards_view.py
import typing
import logging
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from cosmic_event.gui.game_control.progression_controller import CosmicProgressionController
from cosmic_event.gui.impl.gen.view_models.views.lobby.rewards_view.rewards_view_model import RewardsViewModel
from cosmic_event.gui.impl.lobby.quest_packer import getCosmicBonusPacker
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import TypeVar, List, Optional
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.server_events.event_items import Quest
    from frameworks.wulf import ViewEvent, Window
    SimpleBonusesType = TypeVar('SimpleBonusesType', bound=SimpleBonus)
_logger = logging.getLogger(__name__)

class BonusesView(ViewImpl):
    __slots__ = ('_tooltips',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BonusesView, self).__init__(*args, **kwargs)
        self._tooltips = {}

    def _initRewardsList(self, model, quests):
        bonuses = self._getBonuses(quests)
        packerFactory = getCosmicBonusPacker()
        bonusArray = model.getRewards()
        bonusArray.clear()
        bonusArray.reserve(len(bonuses))
        packBonusModelAndTooltipData(bonuses, bonusArray, self._tooltips, packerFactory)
        bonusArray.invalidate()

    def _getBonuses(self, quests):
        raise NotImplementedError()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self._tooltips[tooltipId], self.getParentWindow()) if tooltipId is not None and tooltipId in self._tooltips else None
            if window is not None:
                window.load()
            return window
        elif event.contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = event.getArgument('showCount')
            if showCount is None:
                return
            packedBonuses = self.viewModel.getRewards()[int(showCount):]
            window = DecoratedTooltipWindow(AdditionalRewardsTooltip(packedBonuses), useDecorator=False)
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
            return window
        else:
            return super(BonusesView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipId = event.getArgument('tooltipId')
            lootBoxIdStr = self._tooltips.get(tooltipId)
            if lootBoxIdStr:
                lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxIdStr))
                return LootboxTooltip(lootBox)
        return super(BonusesView, self).createToolTipContent(event=event, contentID=contentID)


class RewardsView(BonusesView):
    __slots__ = ()
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.cosmic_event.lobby.rewards_view.RewardsView())
        settings.flags = ViewFlags.VIEW
        settings.model = RewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardsView, self).getViewModel()

    def _onLoading(self, quests, *args, **kwargs):
        super(RewardsView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self._initRewardsList(model, quests)
            self._initTexts(model, quests)

    def _initialize(self, *args, **kwargs):
        super(RewardsView, self)._initialize(*args, **kwargs)
        self._initListeners()

    def _initListeners(self):
        self.viewModel.onCloseButtonClick += self.onClose
        self.viewModel.onContinueButtonClick += self.onClose

    def _initTexts(self, model, quests):
        progressionStage = self._cosmicProgression.getProgressionStage(quests[0])
        if progressionStage is not None:
            model.setDisplayRewardsCount(True)
            model.setSubtitle(R.strings.cosmicEvent.rewardsView.viewTitle())
            model.setTitle(R.strings.cosmicEvent.rewardsView.stepCompleted())
            model.setProgressionStage(progressionStage)
        else:
            model.setDisplayRewardsCount(False)
            subTitle = R.strings.cosmicEvent.rewardsView.conditionsFulfilledTitle()
            title = R.strings.cosmicEvent.rewardsView.rewardsReceived.title()
            infoText = R.strings.cosmicEvent.rewardsView.rewardsReceived.text()
            if len(quests) == 1:
                title = R.strings.cosmicEvent.rewardsView.rewardReceived.title()
                questNumber = self._cosmicProgression.getAchievementNumber(quests[0])
                if questNumber == 1:
                    subTitle = R.strings.cosmicEvent.rewardsView.allDailyCompleted()
                    infoText = R.strings.cosmicEvent.rewardsView.rewardReceived.text()
                elif questNumber == 2:
                    subTitle = R.strings.cosmicEvent.rewardsView.progressionComplete.title()
                    infoText = R.strings.cosmicEvent.rewardsView.progressionComplete.text()
            model.setSubtitle(subTitle)
            model.setTitle(title)
            model.setInfoText(infoText)
        return

    def _finalize(self):
        self.viewModel.onCloseButtonClick -= self.onClose
        self.viewModel.onContinueButtonClick -= self.onClose

    def onClose(self, *args, **kwargs):
        self.destroyWindow()

    def _getBonuses(self, quests):
        results = []
        for quest in quests:
            results.extend(quest.getBonuses())

        return results


class RewardsWindow(LobbyNotificationWindow):

    def __init__(self, *args, **kwargs):
        super(RewardsWindow, self).__init__(wndFlags=(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN), content=RewardsView(kwargs.pop('quests')), *args, **kwargs)
