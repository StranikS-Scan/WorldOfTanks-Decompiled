# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_rewards_view.py
from account_helpers.AccountSettings import FESTIVAL_REWARDS_VISITED, AccountSettings
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.item_info import FestivalItemInfo
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import AdaptiveSizeCurtailingAwardsComposer
from gui.impl.backport.backport_tooltip import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_rewards_renderer import FestivalRewardsRenderer
from gui.impl.gen.view_models.views.lobby.festival.festival_rewards_view_model import FestivalRewardsViewModel
from gui.impl.gen.view_models.views.lobby.festival.festival_reward_renderer_model import FestivalRewardRendererModel
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import AWARDS_SIZES
from bonus_constants import BonusName
from helpers import dependency
from items import festival
from items.components.festival_constants import FEST_ITEM_TYPE
from skeletons.festival import IFestivalController
from skeletons.gui.server_events import IEventsCache
_DISPLAYED_BONUSES = 5

class _ProgressRewardPresenter(object):
    __festController = dependency.descriptor(IFestivalController)
    __eventsCache = dependency.descriptor(IEventsCache)
    _BONUSES_ORDER = (BonusName.FESTIVAL_ITEMS,
     'dossier',
     'crewSkins',
     'customization')
    __slots__ = ('__progressReward', '__itemsData')

    def __init__(self, progressReward):
        self.__progressReward = progressReward
        self.__itemsData = {}

    def getTooltipData(self, tooltipID):
        return self.__itemsData.get(tooltipID)

    def getRenderer(self):
        renderer = FestivalRewardsRenderer()
        self.updateRenderer(renderer, init=True)
        return renderer

    def updateRenderer(self, renderer, init=False):
        with renderer.transaction() as tx:
            if init:
                self.__makeRewardsGroup(tx)
            reachValue = self.__progressReward.getReachValue()
            tx.setIsAchieved(self.__festController.getReceivedItemsCount() >= reachValue)
            tx.setReachValue(reachValue)

    def __makeRewardsGroup(self, renderer):
        bonuses = self.__eventsCache.getQuestByID(self.__progressReward.getTokenID()).getBonuses()
        rewards = renderer.getItems()
        rewards.clear()
        formattedBonuses = AdaptiveSizeCurtailingAwardsComposer(_DISPLAYED_BONUSES).getFormattedBonuses(bonuses, compareMethod=self.__compareBonuses)
        for index, bonus in enumerate(formattedBonuses):
            reward = FestivalRewardRendererModel()
            icons = reward.getIcons()
            icons.clear()
            icons.addString(bonus.get('imgSource', {}).get(AWARDS_SIZES.SMALL))
            icons.addString(bonus.get('imgSource', {}).get(AWARDS_SIZES.BIG))
            icons.invalidate()
            reward.setLabelStr(bonus.get('label') or '')
            bonusName = bonus.get('bonusName', '')
            reward.setItemName(bonus.get('userName', '') if bonusName == BonusName.FESTIVAL_ITEMS else '')
            reward.setTooltipId(index)
            reward.setHighlightType(bonus.get('highlightIcon') or '')
            reward.setOverlayType(bonus.get('overlayIcon') or '')
            reward.setHasCompensation(bonus.get('hasCompensation') or False)
            reward.setLabelAlign(bonus.get('align') or 'center')
            rewards.addViewModel(reward)
            self.__itemsData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

        rewards.invalidate()
        return

    def __compareBonuses(self, bonus1, bonus2):
        if bonus1.bonusName not in self._BONUSES_ORDER and bonus2.bonusName not in self._BONUSES_ORDER:
            return cmp(bonus1.bonusName, bonus2.bonusName)
        if bonus1.bonusName not in self._BONUSES_ORDER:
            return 1
        if bonus2.bonusName not in self._BONUSES_ORDER:
            return -1
        if bonus1.bonusName == bonus2.bonusName and bonus1.bonusName == BonusName.FESTIVAL_ITEMS:
            itemID = bonus1.specialArgs[0]
            festItem = FestivalItemInfo(itemID)
            if festItem.getType() == FEST_ITEM_TYPE.RANK:
                return -1
            return 1
        return self._BONUSES_ORDER.index(bonus1.bonusName) - self._BONUSES_ORDER.index(bonus2.bonusName)


class FestivalRewardsView(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__progressRewards',)

    def __init__(self, *args, **kwargs):
        super(FestivalRewardsView, self).__init__(R.views.lobby.festival.festival_rewards_view.FestivalRewardsView(), ViewFlags.VIEW, FestivalRewardsViewModel, *args, **kwargs)
        self.__progressRewards = []

    @property
    def viewModel(self):
        return super(FestivalRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipID = event.getArgument('tooltipId')
            levelID = event.getArgument('levelID')
            window = None
            if levelID is not None and tooltipID is not None:
                tooltipData = self.__progressRewards[int(levelID)].getTooltipData(int(tooltipID))
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
            return window
        else:
            return super(FestivalRewardsView, self).createToolTip(event)

    def _initialize(self):
        super(FestivalRewardsView, self)._initialize()
        self.__festController.onDataUpdated += self.__onDataUpdated
        self.__eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self.__createData()
        AccountSettings.setNotifications(FESTIVAL_REWARDS_VISITED, True)

    def _finalize(self):
        self.__progressRewards = None
        self.__festController.onDataUpdated -= self.__onDataUpdated
        self.__eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        super(FestivalRewardsView, self)._finalize()
        return

    def __onDataUpdated(self, keys):
        if FestSyncDataKeys.ITEMS in keys:
            self.__updateData()

    def __onQuestsUpdated(self, *_):
        self.__updateData()

    def __createData(self):
        for progressReward in festival.g_cache.getProgressRewards():
            self.__progressRewards.append(_ProgressRewardPresenter(progressReward))

        with self.viewModel.transaction() as tx:
            renderers = tx.getRewards()
            renderers.clear()
            for progressRewardPresenter in self.__progressRewards:
                renderer = progressRewardPresenter.getRenderer()
                renderers.addViewModel(renderer)

            renderers.invalidate()
            self.__updateItems(tx)

    def __updateItems(self, model):
        model.setReceivedItems(self.__festController.getReceivedItemsCount())
        model.setTotalItems(self.__festController.getTotalItemsCount())

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            renderers = tx.getRewards()
            for idx, renderer in enumerate(renderers):
                self.__progressRewards[idx].updateRenderer(renderer)

            self.__updateItems(tx)
