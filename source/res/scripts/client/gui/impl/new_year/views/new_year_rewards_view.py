# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_rewards_view.py
import logging
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingByTypeAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport_tooltip import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.components.ny_reward_renderer.ny_secondary_reward_renderer_model import NySecondaryRewardRendererModel
from gui.impl.gen.view_models.new_year.components.new_year_rewards_renderer_model import NewYearRewardsRendererModel
from gui.impl.gen.view_models.new_year.views.new_year_rewards_view_model import NewYearRewardsViewModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared.event_dispatcher import showNewYearApplyVehicleDiscount, showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import int2roman, dependency
from items.components.ny_constants import CustomizationObjects
from items.tankmen import getNationGroups
from new_year.ny_level_helper import NewYearAtmospherePresenter, getLevelIndexes
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from gui.shared.gui_items.Vehicle import getIconResource
from new_year.ny_constants import Collections
from skeletons.gui.game_control import IFestivityController
_logger = logging.getLogger(__name__)
_REWARDS_TOOLTIP_KEY = 'rewardsKey'
_TANKMAN_TOOLTIP_KEY = 'tankmanKey'
_DISPLAYED_BONUSES = ('dossier',)

def _checkTankmanGroup(tankmanDesc, groupName):
    groups = getNationGroups(tankmanDesc.nationID, tankmanDesc.isPremium)
    return groups[tankmanDesc.gid].name == groupName


class _LevelRewardPresenter(object):
    __slots__ = ('__levelInfo', '__itemsData')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, level):
        self.__levelInfo = self._nyController.getLevel(level)
        self.__itemsData = {}

    def createToolTip(self, key, index, parentWindow):
        tooltipData = None
        if key == _REWARDS_TOOLTIP_KEY and index is not None:
            tooltipData = self.__itemsData[index]
        elif key == _TANKMAN_TOOLTIP_KEY:
            tooltipData = self.__getTankmanTooltipData()
        if tooltipData is not None:
            window = BackportTooltipWindow(tooltipData, parentWindow)
            window.load()
            return window
        else:
            return

    def getRenderer(self, idx):
        renderer = NewYearRewardsRendererModel()
        renderer.setIsLastLevel(self.__levelInfo.isLastLevel())
        renderer.setIsNewYearEnabled(self._nyController.isEnabled())
        renderer.setIdx(idx)
        self.__makeRewardsGroup(renderer, idx)
        self.updateRenderer(renderer)
        return renderer

    def updateRenderer(self, renderer):
        with renderer.transaction() as tx:
            tx.setIsCurrentLevel(self.__levelInfo.isCurrent())
            tx.setIsLevelAchieved(self.__levelInfo.isAchieved())
            isNextAfterCurrent = self.__levelInfo.level() - 1 == NewYearAtmospherePresenter.getLevel()
            tx.setIsNextAfterCurrentLevel(isNextAfterCurrent)
            tx.setLevelIcon(self.__getLevelIcon())
            tx.setLevelText(self.__getLevelText())
            tx.tankReward.setTierText(int2roman(self.__levelInfo.level()))
            tx.tankReward.setDiscountText(self.__getDiscountText())
            vehicle = self.__levelInfo.getSelectedVehicle()
            tx.tankReward.setIsApplied(self.__levelInfo.discountApplied())
            if vehicle is not None:
                tx.tankReward.setIsGifted(self.__levelInfo.hasGiftedVehicle())
                tx.tankReward.setRewardImage(getIconResource(vehicle.name))
                tx.tankReward.setNameText(vehicle.userName)
                tx.tankReward.setTierText(int2roman(vehicle.level))
            tx.setShowTankwoman(self.__levelInfo.hasTankman())
            tx.tankwomanReward.setIsApplied(self.__levelInfo.tankmanIsRecruited())
            if self.__levelInfo.tankmanIsRecruited():
                tx.tankwomanReward.setRewardImage(self.__getTankwomanIcon())
        return

    def recruitTankwoman(self):
        if self.__levelInfo.hasTankman() and not self.__levelInfo.tankmanIsRecruited():
            showRecruitWindow(self.__levelInfo.getTankmanToken())
        else:
            _logger.error('Recruit tankwoman when tankwoman has not in account')

    def applyDiscount(self):
        showNewYearApplyVehicleDiscount(self.__levelInfo.level())

    def clear(self):
        self.__levelInfo = None
        self.__itemsData.clear()
        return

    def __getLevelIcon(self):
        if self.__levelInfo.isCurrent():
            return R.images.gui.maps.icons.new_year.widget.levels.c_80x80.dyn('level{}'.format(self.__levelInfo.level()))
        return R.images.gui.maps.icons.new_year.rewards_view.circle_active if self.__levelInfo.isAchieved() else R.images.gui.maps.icons.new_year.rewards_view.circle_notactive

    def __getLevelText(self):
        return '' if self.__levelInfo.isCurrent() else int2roman(self.__levelInfo.level())

    def __getDiscountText(self):
        discountValue = self.__levelInfo.variadicDiscountValue()
        return str(discountValue) if discountValue is not None else ''

    def __getTankwomanIcon(self):
        recruitInfo = self.__levelInfo.getTankmanInfo()
        iconName = recruitInfo.getSmallIcon().replace('.png', '').replace('-', '_')
        return R.images.gui.maps.icons.tankmen.icons.big.dyn(iconName)

    def __makeRewardsGroup(self, renderer, idx):
        bonuses = [ bonus for bonus in self.__levelInfo.getBonuses() if bonus.getName() != 'vehicles' ]
        rewards = renderer.rewardsGroup.getItems()
        rewards.clear()
        formattedBonuses = CurtailingByTypeAwardsComposer(_DISPLAYED_BONUSES).getFormattedBonuses(bonuses)
        for index, bonus in enumerate(formattedBonuses):
            reward = NySecondaryRewardRendererModel()
            with reward.transaction() as rewardTx:
                rewardTx.setIcon(bonus.get('imgSource', ''))
                rewardTx.setIdx(idx)
                rewardTx.setTooltipId(index)
            rewards.addViewModel(reward)
            self.__itemsData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

        return

    def __getTankmanTooltipData(self):
        tooltipData = None
        if self.__levelInfo.tankmanIsRecruited():
            tankmen = self._itemsCache.items.inventory.getItemsData(GUI_ITEM_TYPE.TANKMAN)
            for invID, tankman in tankmen.iteritems():
                if _checkTankmanGroup(tankman.descriptor, self.__levelInfo.getTankmanInfo().getGroupName()):
                    tooltipData = TooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN, specialArgs=[invID], tooltip=None)
                    break

        else:
            tooltipData = TooltipData(isSpecial=True, tooltip=None, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[self.__levelInfo.getTankmanToken()])
        return tooltipData


class NewYearRewardsView(NewYearNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    __slots__ = ('__blur', '__levels')

    def __init__(self, *args, **kwargs):
        super(NewYearRewardsView, self).__init__(R.views.newYearRewardsView, ViewFlags.LOBBY_SUB_VIEW, NewYearRewardsViewModel, *args, **kwargs)
        self.__levels = []
        self.__blur = WGUIBackgroundBlurSupportImpl(blurUI=False)

    @property
    def viewModel(self):
        return super(NewYearRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent:
            key = event.getArgument('key')
            tooltipId = event.getArgument('tooltipId')
            idx = int(event.getArgument('idx'))
            window = None
            if idx is not None:
                window = self.__levels[idx].createToolTip(key, tooltipId, self.getParentWindow())
            return window
        else:
            return super(NewYearRewardsView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.REWARDS_ATMOSPHERE,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.REWARDS_ATMOSPHERE_2019_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_ATMOSPHERE}
        super(NewYearRewardsView, self)._initialize(soundConfig)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onTankDiscountClick += self.__onTankDiscountClick
        self.viewModel.onTankwomanRecruitClick += self.__onTankwomanRecruitClick
        self.viewModel.onAlbumClick += self.__onAlbumClick
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self.__blur.enable()
        self.__createData()

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onTankDiscountClick -= self.__onTankDiscountClick
        self.viewModel.onTankwomanRecruitClick -= self.__onTankwomanRecruitClick
        self.viewModel.onAlbumClick -= self.__onAlbumClick
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        while self.__levels:
            self.__levels.pop().clear()

        self.__blur.disable()
        super(NewYearRewardsView, self)._finalize()

    def _getInfoForHistory(self):
        return {}

    def __onCloseBtnClick(self, _):
        festivityController = dependency.instance(IFestivityController)
        if not festivityController.isEnabled():
            showHangar()
            return
        if not self.getCurrentObject():
            self._navigationState.setIsInternalSwitch(True)
            self.switchByObjectName(CustomizationObjects.FIR)
        else:
            self._goToMainView()

    def __onTankDiscountClick(self, args=None):
        if args is None or 'idx' not in args:
            return
        else:
            idx = int(args['idx'])
            self.__levels[idx].applyDiscount()
            return

    def __onTankwomanRecruitClick(self, args=None):
        if args is None or 'idx' not in args:
            return
        else:
            idx = int(args['idx'])
            self.__levels[idx].recruitTankwoman()
            return

    def __onAlbumClick(self):
        self._goToAlbumView(collectionName=Collections.NewYear18)

    def __onCacheResync(self, *_):
        self.__updateData()

    def __createData(self):
        for level in getLevelIndexes():
            self.__levels.append(_LevelRewardPresenter(level))

        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            renderers.clear()
            for idx, levelPresenter in enumerate(self.__levels):
                renderer = levelPresenter.getRenderer(idx)
                renderers.addViewModel(renderer)

            tx.setCurrentLvl(NewYearAtmospherePresenter.getLevel())

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            for idx, renderer in enumerate(renderers):
                self.__levels[idx].updateRenderer(renderer)

            tx.setCurrentLvl(NewYearAtmospherePresenter.getLevel())
