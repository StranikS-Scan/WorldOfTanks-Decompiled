# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/rewards_views/races_rewards_view.py
import logging
import typing
from gui.server_events.bonuses import mergeBonuses
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from races.gui.game_control.progression_controller import RacesProgressionController
from races.gui.impl.gen.view_models.views.lobby.reward_view.reward_view_model import RewardViewModel
from races.gui.impl.lobby.races_lobby_view.races_progression_view import getRacesBonusPacker
from races.skeletons.progression_controller import IRacesProgressionController
from races.gui.shared.bonus_helpers import sortBonuses, getMergeRacesBonusFunction
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_helper import getKeyByID
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import findFirst
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
MAIN_BONUSES = ['crystal']
_TWO_STAGES_REWARDS_COUNT = 2
_PEDESTAL_REWARDS_COUNT = 3

def splitMainAdditionalBonuses(bonuses, quests):
    bonuses = sortBonuses(mergeBonuses(bonuses, getMergeFunc=getMergeRacesBonusFunction))
    mainBonuses = []
    additionalBonuses = []
    if len(quests) == 1:
        mainBonuses = bonuses
    if len(quests) == 2:
        mainRewardsLen = _PEDESTAL_REWARDS_COUNT if findFirst(lambda b: b.getName() == 'dossier', bonuses) is not None else _TWO_STAGES_REWARDS_COUNT
        mainBonuses = bonuses[:mainRewardsLen]
        additionalBonuses = bonuses[mainRewardsLen:]
    if len(mainBonuses) == _PEDESTAL_REWARDS_COUNT:
        mainBonuses[0], mainBonuses[1] = mainBonuses[1], mainBonuses[0]
    return (mainBonuses, additionalBonuses)


class BonusesView(ViewImpl):
    __slots__ = ('_tooltips',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BonusesView, self).__init__(*args, **kwargs)
        self._tooltips = {}

    def _initRewardsList(self, model, quests):
        bonuses = self._getBonuses(quests)
        packerFactory = getRacesBonusPacker()
        mainBonuses, additionalBonuses = splitMainAdditionalBonuses(bonuses, quests)
        bonusArray = model.getRewards()
        bonusArray.clear()
        bonusArray.reserve(len(additionalBonuses))
        mainBonusArray = model.getMainRewards()
        mainBonusArray.clear()
        mainBonusArray.reserve(len(mainBonuses))
        packBonusModelAndTooltipData(additionalBonuses, bonusArray, self._tooltips, packerFactory)
        packBonusModelAndTooltipData(mainBonuses, mainBonusArray, self._tooltips, packerFactory)
        bonusArray.invalidate()
        mainBonusArray.invalidate()

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
        tooltipId = event.getArgument('tooltipId')
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            lootBoxIdStr = self._tooltips.get(tooltipId)
            if lootBoxIdStr:
                lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxIdStr))
                return LootboxTooltip(lootBox)
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip():
            tooltipData = self._tooltips.get(tooltipId)
            lootBoxKeyID = tooltipData.get('lootBoxKeyID')
            lootBoxKey = getKeyByID(lootBoxKeyID)
            return LootboxKeyTooltip(lootBoxKey)
        return super(BonusesView, self).createToolTipContent(event=event, contentID=contentID)


class RewardsView(BonusesView):
    __slots__ = ()
    _racesProgression = dependency.descriptor(IRacesProgressionController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.races.lobby.reward_view.RewardView())
        settings.flags = ViewFlags.VIEW
        settings.model = RewardViewModel()
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

    def _getEvents(self):
        return ((self.viewModel.onCloseButtonClick, self.onClose), (self.viewModel.onContinueButtonClick, self.onClose))

    def _initTexts(self, model, quests):
        progressionStages = []
        for quest in quests:
            stage = self._racesProgression.getProgressionStage(quest)
            if stage is not None:
                progressionStages.append(stage)

        rewardsViews = R.strings.races.lobby.views.rewardsViews
        if len(progressionStages):
            if len(quests) == 1:
                model.setSubtitle(rewardsViews.progressionView.subtitle())
            else:
                model.setSubtitle(rewardsViews.multiProgressionView.subtitle())
            model.setTitle(rewardsViews.progressionView.title())
            modelProgressionStages = model.getProgressionStages()
            modelProgressionStages.clear()
            for stage in sorted(progressionStages):
                modelProgressionStages.addNumber(stage)

        else:
            if self._racesProgression.isRacesFirstWinQuest(quests[0].getID()):
                model.setTitle(rewardsViews.firstWinView.title())
                model.setSubtitle(rewardsViews.firstWinView.subtitle())
            else:
                model.setTitle(rewardsViews.firstEntranceView.title())
                model.setSubtitle(rewardsViews.firstEntranceView.subtitle())
            modelProgressionStages = model.getProgressionStages()
            modelProgressionStages.clear()
        return

    def onClose(self, *args, **kwargs):
        self.destroyWindow()

    def _getBonuses(self, quests):
        results = []
        for quest in quests:
            results.extend(quest.getBonuses())

        return results


class RacesRewardsWindow(LobbyNotificationWindow):

    def __init__(self, *args, **kwargs):
        super(RacesRewardsWindow, self).__init__(wndFlags=(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN), content=RewardsView(kwargs.pop('quests')), layer=WindowLayer.OVERLAY, *args, **kwargs)
