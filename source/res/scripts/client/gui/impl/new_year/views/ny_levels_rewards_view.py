# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/ny_levels_rewards_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LootBoxBonusComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_rewards_renderer_model import NewYearRewardsRendererModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_renderer.ny_secondary_reward_renderer_model import NySecondaryRewardRendererModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_levels_rewards_view_model import NyLevelsRewardsViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases, NewYearTabCache
from gui.impl.new_year.new_year_helper import nyBonusSortOrder
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundStates
from gui.impl.new_year.tooltips.ny_talisman_tooltip import NewYearTalismanTooltipContent
from gui.impl.new_year.tooltips.new_year_tank_slot_tooltip import NewYearTankSlotTooltipContent
from gui.server_events.awards_formatters import AWARDS_SIZES, getNYAwardsPacker
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.server_events.recruit_helper import DEFAULT_NY_GIRL
from gui.shared.event_dispatcher import showNewYearVehiclesView
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, int2roman
from items.tankmen import getNationGroups
from new_year.ny_constants import Collections
from new_year.ny_level_helper import NewYearAtmospherePresenter, getLevelIndexes
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, ITalismanSceneController
_logger = logging.getLogger(__name__)
_VISIBLE_COUNT = 6
_MAX_VISIBLE_COUNT = 9
_DEFAULT_ALIGN = 'center'

class _RewardsSubTypes(CONST_CONTAINER):
    TANKWOMAN = 'tankwoman'
    TALISMAN = 'freeTalisman'
    REWARDS = 'rewards'


class _TankmanRewardStates(CONST_CONTAINER):
    STATE_LOCKED = 'locked'
    STATE_OPENED = 'opened'
    STATE_RECEIVED = 'received'


def _checkTankmanGroup(tankmanDesc, groupName):
    groups = getNationGroups(tankmanDesc.nationID, tankmanDesc.isPremium)
    return groups[tankmanDesc.gid].name == groupName


class _LevelRewardPresenter(object):
    __slots__ = ('__index', '__levelInfo', '__itemsData', '__maxCapacity')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _talismanController = dependency.descriptor(ITalismanSceneController)
    _navigationAlias = ViewAliases.REWARDS_VIEW

    def __init__(self, index, level):
        self.__index = index
        self.__itemsData = {}
        self.__levelInfo = self._nyController.getLevel(level)
        self.__maxCapacity = self.__validateCapacity(_VISIBLE_COUNT)

    def createToolTip(self, key, index, parentWindow):
        tooltipData = None
        if key == _RewardsSubTypes.REWARDS and index is not None:
            tooltipData = self.__itemsData[index]
        elif key == _RewardsSubTypes.TANKWOMAN:
            tooltipData = self.__getTankmanTooltipData()
        if tooltipData is not None:
            window = BackportTooltipWindow(tooltipData, parentWindow)
            window.load()
            return window
        else:
            return

    def getRenderer(self):
        renderer = NewYearRewardsRendererModel()
        renderer.setIsLastLevel(self.__levelInfo.isLastLevel())
        renderer.setShowTank(self.__levelInfo.hasTankSlot())
        renderer.setIsMaxReachedLevel(self.__levelInfo.isMaxReachedLevel())
        renderer.setIdx(self.__index)
        self.__makeRewardsGroup(renderer)
        self.updateRenderer(renderer)
        return renderer

    def updateRenderer(self, renderer):
        with renderer.transaction() as tx:
            tx.setIsNewYearEnabled(self._nyController.isEnabled())
            tx.setIsCurrentLevel(self.__levelInfo.isCurrent())
            tx.setIsLevelAchieved(self.__levelInfo.isAchieved())
            isNextAfterCurrent = self.__levelInfo.level() - 1 == NewYearAtmospherePresenter.getLevel()
            tx.setIsNextAfterCurrentLevel(isNextAfterCurrent)
            level = self.__levelInfo.level()
            tx.setLevelText(int2roman(level))
            tx.setTankLevel(level)
            tx.setShowTankwomanTalisman(self.__levelInfo.hasTalisman())
            isTmanRecruited = self.__levelInfo.tankmanIsRecruited()
            tx.setIsTankwomanApplied(isTmanRecruited)
            talismanInfo = self.__levelInfo.getTalismanInfo()
            hasTalisman = talismanInfo is not None
            tx.setIsTalismanApplied(hasTalisman)
            tx.setIsTalismanLocked(not self.__levelInfo.isAchieved())
            if hasTalisman:
                tx.setTalismanImg(backport.image(talismanInfo.getSmallIcon()))
            else:
                tx.setTalismanImg(backport.image(R.images.gui.maps.icons.new_year.talismans.small.default()))
            tx.setIsTankwomanLocked(talismanInfo is None)
        return

    def updateCapacity(self, renderer, maxCapacity):
        self.__maxCapacity = self.__validateCapacity(maxCapacity)
        formattedBonuses = self.__getFormattedBonuses()
        bonusesCount = len(formattedBonuses)
        rewards = renderer.rewardsGroup.getItems()
        prevCapacity = len(rewards)
        if prevCapacity > bonusesCount:
            idxs = range(bonusesCount, prevCapacity)
            rewards.removeValues(idxs)
            for idx in idxs:
                self.__itemsData[idx] = createTooltipData()

        for index, bonus in enumerate(formattedBonuses):
            if prevCapacity > index:
                self.__fillBonusValues(rewards[index], index, bonus)
            rewards.addViewModel(self.__createRewardItem(self.__index, index, bonus))

        renderer.rewardsGroup.invalidate()

    def recruitTankwoman(self):
        talismanInfo = self.__levelInfo.getTalismanInfo()
        if talismanInfo is not None and not self.__levelInfo.tankmanIsRecruited():
            showRecruitWindow(talismanInfo.getTankmanToken())
        else:
            _logger.error('Recruit tankwoman when tankwoman has not in account')
        return

    def onTalismanClick(self):
        self._talismanController.switchToPreview()

    def clear(self):
        self.__levelInfo = None
        self.__itemsData.clear()
        return

    def __makeRewardsGroup(self, renderer):
        rewards = renderer.rewardsGroup.getItems()
        rewards.clear()
        formattedBonuses = self.__getFormattedBonuses()
        rewards.reserve(_MAX_VISIBLE_COUNT)
        for index, bonus in enumerate(formattedBonuses):
            rewards.addViewModel(self.__createRewardItem(self.__index, index, bonus))

    def __createRewardItem(self, groupIdx, index, bonus):
        reward = NySecondaryRewardRendererModel()
        with reward.transaction() as rewardTx:
            rewardTx.setIdx(groupIdx)
            rewardTx.setTooltipId(index)
            self.__fillBonusValues(rewardTx, index, bonus)
        return reward

    def __fillBonusValues(self, rewardItem, index, bonus):
        rewardItem.setIcon(bonus.get('imgSource') or '')
        rewardItem.setLabelStr(bonus.get('label') or '')
        rewardItem.setLabelAlign(bonus.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
        rewardItem.setHighlightType(bonus.get('highlightIcon') or '')
        rewardItem.setOverlayType(bonus.get('overlayIcon') or '')
        rewardItem.setIsHidden(False)
        self.__itemsData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))
        return

    def __getFormattedBonuses(self):
        bonuses = self.__levelInfo.getBonuses()
        bonuses.sort(key=nyBonusSortOrder)
        formatter = LootBoxBonusComposer(self.__maxCapacity, getNYAwardsPacker())
        return formatter.getVisibleFormattedBonuses(bonuses, [], AWARDS_SIZES.SMALL)

    def __getTankmanTooltipData(self):
        tooltipData = None
        if self.__levelInfo.tankmanIsRecruited():
            tankmen = self._itemsCache.items.inventory.getItemsData(GUI_ITEM_TYPE.TANKMAN)
            for invID, tankman in tankmen.iteritems():
                if _checkTankmanGroup(tankman.descriptor, self.__levelInfo.getTankmanInfo().getGroupName()):
                    tooltipData = TooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN, specialArgs=[invID], tooltip=None)
                    break

        else:
            talismanInfo = self.__levelInfo.getTalismanInfo()
            tooltipData = TooltipData(isSpecial=True, tooltip=None, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[DEFAULT_NY_GIRL, talismanInfo is None])
        return tooltipData

    def __validateCapacity(self, newValue):
        newCapacity = newValue
        if self.__levelInfo.hasTankSlot():
            newCapacity -= 1
        if self.__levelInfo.hasTalisman():
            newCapacity -= 2
        if self.__levelInfo.isLastLevel():
            newCapacity -= 1
        return newCapacity


class NyLevelsRewardsView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _isScopeWatcher = False
    __slots__ = ('__levels', '__maxCapacity')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.ny_levels_rewards_view.NyLevelsRewardsView())
        settings.model = NyLevelsRewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyLevelsRewardsView, self).__init__(settings)
        self.__levels = []
        self.__maxCapacity = _VISIBLE_COUNT

    @property
    def viewModel(self):
        return super(NyLevelsRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            key = event.getArgument('key')
            tooltipId = event.getArgument('tooltipId')
            idx = int(event.getArgument('idx'))
            window = None
            if idx is not None:
                window = self.__levels[idx].createToolTip(key, tooltipId, self.getParentWindow())
            return window
        else:
            return super(NyLevelsRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.ny_talisman_tooltip.NewYearTalismanTooltipContent():
            idx = int(event.getArgument('idx')) + 1
            return NewYearTalismanTooltipContent(level=idx)
        if ctID == R.views.lobby.new_year.tooltips.new_year_tank_slot_tooltip.NewYearTankSlotTooltipContent():
            idx = int(event.getArgument('idx')) + 1
            return NewYearTankSlotTooltipContent(level=idx, levelName=int2roman(idx))
        return super(NyLevelsRewardsView, self).createToolTipContent(event, ctID)

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_LEVELS}
        super(NyLevelsRewardsView, self)._initialize(soundConfig)
        self.viewModel.onTankSlotClick += self.__onTankSlotClick
        self.viewModel.onTankwomanClick += self.__onTankwomanClick
        self.viewModel.onTalismanClick += self.__onTalismanClick
        self.viewModel.onRewardsCapacityChanged += self.__onRewardsCapacityChanged
        self.viewModel.onAlbumClick += self.__onAlbumClick
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self.__createData()

    def _finalize(self):
        self.viewModel.onTankSlotClick -= self.__onTankSlotClick
        self.viewModel.onTankwomanClick -= self.__onTankwomanClick
        self.viewModel.onTalismanClick -= self.__onTalismanClick
        self.viewModel.onRewardsCapacityChanged -= self.__onRewardsCapacityChanged
        self.viewModel.onAlbumClick -= self.__onAlbumClick
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        while self.__levels:
            self.__levels.pop().clear()

        super(NyLevelsRewardsView, self)._finalize()

    def _getInfoForHistory(self):
        return {}

    def __onTalismanClick(self, args=None):
        if args is None or 'idx' not in args:
            return
        else:
            idx = int(args['idx'])
            self.__levels[idx].onTalismanClick()
            return

    def __onTankwomanClick(self, args=None):
        if args is None or 'idx' not in args:
            return
        else:
            idx = int(args['idx'])
            self.__levels[idx].recruitTankwoman()
            return

    def __onCacheResync(self, *_):
        self.__updateData()

    def __createData(self):
        for index, level in enumerate(getLevelIndexes()):
            self.__levels.append(_LevelRewardPresenter(index, level))

        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            renderers.clear()
            for levelPresenter in self.__levels:
                renderer = levelPresenter.getRenderer()
                renderers.addViewModel(renderer)

            renderers.invalidate()
            tx.setCurrentLvl(NewYearAtmospherePresenter.getLevel())

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            for idx, renderer in enumerate(renderers):
                self.__levels[idx].updateRenderer(renderer)

            tx.setCurrentLvl(NewYearAtmospherePresenter.getLevel())

    def __onTankSlotClick(self):
        showNewYearVehiclesView()

    def __onRewardsCapacityChanged(self, args):
        self.__maxCapacity = int(args.get('maxCapacity', _VISIBLE_COUNT))
        self.__updateCapacity()

    def __updateCapacity(self):
        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            for idx, renderer in enumerate(renderers):
                self.__levels[idx].updateCapacity(renderer, self.__maxCapacity)

    def __onAlbumClick(self):
        self._goToAlbumView(yearName=Collections.NewYear19, stateInfo=(NewYearTabCache.COVER_STATE, {}))
