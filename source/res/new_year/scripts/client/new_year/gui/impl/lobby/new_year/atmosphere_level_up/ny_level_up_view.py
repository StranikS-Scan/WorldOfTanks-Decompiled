# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/atmosphere_level_up/ny_level_up_view.py
import logging
from functools import partial
import enum
import typing
import AnimationSequence
import BigWorld
from frameworks.wulf import ViewSettings, WindowLayer, ViewStatus, WindowStatus
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl import backport
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.atmosphere_level_up_model import AtmosphereLevelUpModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from new_year.gui.impl.lobby.new_year.tooltips.ny_marketplace_token_tooltip import NyMarketplaceTokenTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_menu_collections_tooltip import NyMenuCollectionsTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from new_year.gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from new_year.gui.impl.new_year.new_year_helper import nyBonusGFSortOrder, ADDITIONAL_BONUS_NAME_GETTERS
from new_year.gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from new_year.gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from new_year.gui.shared.event_dispatcher import showVehicleDiscountOverlay
from new_year.ny_constants import ViewAliases
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import splitBonuses
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, uniprof, isPlayerAccount
from new_year_common.items.components.ny_constants import CurrentNYConstants, YEARS_INFO
from messenger.proto.events import g_messengerEvents
from skeletons.gui.impl import IGuiLoader, INotificationWindowController, INewYearNavigation
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController
from uilogging.deprecated.decorators import loggerEntry
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_FIRST_LVL = 1
_HUGE_BONUESES_ORDER = ('lootBoxToken',
 'tmanToken',
 'variadicDiscount',
 'vehicles',
 'customizations',
 'premium_plus',
 'customizations_style',
 CurrentNYConstants.FILLERS,
 'dossier')

class _RewardType(enum.Enum):
    COLLECTION = 'collection'
    ATMOSPHERE = 'atmosphere'


def _splitHugeBonuses(bonuses, maxHugeBonuses):
    hugeBonuses = []
    otherBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(bonus)
        if bonusName in _HUGE_BONUESES_ORDER:
            hugeBonuses.append(bonus)
        otherBonuses.append(bonus)

    if len(hugeBonuses) > 1:
        hugeBonuses.sort(key=_hugeBonusesSortOrder)
        otherBonuses.extend(hugeBonuses[maxHugeBonuses:])
        hugeBonuses = hugeBonuses[:maxHugeBonuses]
    return (hugeBonuses, otherBonuses)


def _hugeBonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _HUGE_BONUESES_ORDER.index(bonusName) if bonusName in _HUGE_BONUESES_ORDER else len(_HUGE_BONUESES_ORDER)


def _getCollectionName(collectionStrID):
    return '_'.join(YEARS_INFO.getCollectionSettingNameAndYear(collectionStrID))


class NyAtmosphereLevelUpView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gui = dependency.descriptor(IGuiLoader)
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __SPLITTERS_BY_REWARD_TYPE = {_RewardType.COLLECTION: partial(_splitHugeBonuses, maxHugeBonuses=2),
     _RewardType.ATMOSPHERE: partial(_splitHugeBonuses, maxHugeBonuses=3)}

    def __init__(self, backCallback=None, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.AtmosphereLevelUp())
        settings.model = AtmosphereLevelUpModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyAtmosphereLevelUpView, self).__init__(settings)
        self.__tooltips = {}
        self.__rewards = {}
        self.__currentRewardId = 0
        self.__currentRewardType = None
        self.__completedLevels = []
        self.__completedCollections = []
        self.__backCallback = backCallback
        return

    @property
    def viewModel(self):
        return super(NyAtmosphereLevelUpView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyMenuCollectionsTooltip():
            return NyMenuCollectionsTooltip()
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyShardsTooltip():
            return NyShardsTooltip()
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyMarketplaceTokenTooltip():
            return NyMarketplaceTokenTooltip()
        if ctID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        if ctID == R.views.new_year.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            variadicID, discount = event.getArgument('variadicID'), event.getArgument('discount')
            return NyDiscountRewardTooltip(variadicID, discount)
        if R.views.dyn('gui_lootboxes').isValid() and ctID == R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__tooltips[event.getArgument('tooltipId')]
            return tooltipData.tooltip(*tooltipData.specialArgs)
        if ctID == R.views.lobby.tooltips.AdditionalRewardsTooltip() and self.viewStatus == ViewStatus.LOADED:
            showCount = int(event.getArgument('showedCount'))
            bonuses = splitBonuses(self.__rewards[self.__currentRewardId])
            splitter = self.__SPLITTERS_BY_REWARD_TYPE[self.__currentRewardType]
            _, secondaryBonuses = splitter(bonuses)
            return AdditionalRewardsTooltip(sorted(secondaryBonuses, key=nyBonusGFSortOrder)[showCount:], getNewYearBonusPacker())
        return super(NyAtmosphereLevelUpView, self).createToolTipContent(event, ctID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NyAtmosphereLevelUpView, self).createToolTip(event)

    def appendRewards(self, *_, **kwargs):
        for level, rewards in kwargs.get('levelRewards', {}).iteritems():
            self.__rewards[level] = rewards
            self.__completedLevels.append(level)

        for collection, rewards in kwargs.get('collectionRewards', {}).iteritems():
            self.__rewards[collection] = rewards
            self.__completedCollections.append(collection)

        self.__completedLevels.sort()
        self.__completedCollections.sort(key=YEARS_INFO.getCollectionIntID)
        if not self.__currentRewardId:
            self.__processNextReward()

    def _onLoading(self, *_, **kwargs):
        super(NyAtmosphereLevelUpView, self)._onLoading()
        self.viewModel.onClose += self.__onCloseAction
        self.viewModel.onGotoStore += self.__onGoToStore
        self.viewModel.onGotoQuests += self.__onGoToQuests
        self.viewModel.onSelectVehicleDiscount += self.__onSelectVehicleDiscount
        self.__nyController.onStateChanged += self.__onEventStateChanged
        self.__nyController.onDataUpdated += self.__onDataUpdated
        if not self.__hasRewards:
            self.viewModel.setIsViewReady(False)
        elif not self.__currentRewardId:
            self.__processNextReward()
        if self.__nyController.isMaxAtmosphereLevel():
            self.__unlockMachineShopNotification()

    def __hasRewards(self):
        return bool(set(self.__completedLevels + self.__completedCollections).intersection(self.__rewards.keys()))

    def __onDataUpdated(self, *_):
        self.__setRewards()

    def __processNextReward(self):
        if self.__completedLevels:
            self.__currentRewardId = self.__completedLevels.pop(0)
            self.__currentRewardType = _RewardType.ATMOSPHERE
        elif self.__completedCollections:
            self.__currentRewardId = self.__completedCollections.pop(0)
            self.__currentRewardType = _RewardType.COLLECTION
        if self.__currentRewardId:
            self.__setRewards()

    @loggerEntry
    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NyAtmosphereLevelUpView, self)._initialize(*args, **kwargs)
        setOverlayHangarGeneral(True)
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)

    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='exit')
    def _finalize(self):
        g_messengerEvents.onUnlockPopUpMessages()
        setOverlayHangarGeneral(False)
        super(NyAtmosphereLevelUpView, self)._finalize()
        self.viewModel.onClose -= self.__onCloseAction
        self.viewModel.onGotoStore -= self.__onGoToStore
        self.viewModel.onGotoQuests -= self.__onGoToQuests
        self.viewModel.onSelectVehicleDiscount -= self.__onSelectVehicleDiscount
        self.__nyController.onStateChanged -= self.__onEventStateChanged
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        self.__rewards = None
        self.__nyController.updateVariadicDiscounts()
        return

    def __onCloseAction(self):
        if self.__hasRewards():
            self.__processNextReward()
            return
        else:
            if callable(self.__backCallback) and isPlayerAccount():
                self.__backCallback()
            self.__backCallback = None
            self.destroyWindow()
            return

    def __goToView(self, viewAlias):
        if self.__hasRewards():
            _logger.error('Not all rewards viewed')
        self.__newYearNavigation.showNavigationView(viewAlias)
        self.destroyWindow()

    def __onGoToStore(self):
        self.__goToView(ViewAliases.SURPRISE_MACHINE_VIEW)

    def __onGoToQuests(self):
        self.__goToView(ViewAliases.QUESTS_VIEW)

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __onSelectVehicleDiscount(self):
        showVehicleDiscountOverlay()

    def __setRewards(self):
        bonuses = self.__rewards[self.__currentRewardId]
        bonuses = splitBonuses(bonuses)
        splitter = self.__SPLITTERS_BY_REWARD_TYPE[self.__currentRewardType]
        hugeBonuses, otherBonuses = splitter(bonuses)
        with self.getViewModel().transaction() as model:
            self.__tooltips.clear()
            self.__fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=_hugeBonusesSortOrder, packer=getNewYearBonusPacker())
            self.__fillRewardsList(rewardsList=model.rewards.getItems(), bonuses=otherBonuses, sortMethod=nyBonusGFSortOrder, packer=getNewYearBonusPacker())
            if self.__currentRewardType == _RewardType.ATMOSPHERE:
                model.setLevel(self.__currentRewardId)
                model.setCollection('')
            elif self.__currentRewardType == _RewardType.COLLECTION:
                model.setLevel(0)
                model.setCollection(_getCollectionName(self.__currentRewardId))
            model.setIsViewReady(True)

    def __fillRewardsList(self, rewardsList, bonuses, sortMethod, packer):
        rewardsList.clear()
        bonuses.sort(key=sortMethod)
        packBonusModelAndTooltipData(bonuses, rewardsList, packer, self.__tooltips)
        rewardsList.invalidate()

    def __unlockMachineShopNotification(self):
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.purchase.text()), type=SM_TYPE.NewYearMachine, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.machine.purchase.header())})


class NyLevelUpWindow(LobbyNotificationWindow):
    __slots__ = ('__blurBackground', '__worldDrawEnabled', '__worldOn', '__blur')

    def __init__(self, layer=WindowLayer.OVERLAY, blurBackground=False, worldDrawEnabled=False, *args, **kwargs):
        super(NyLevelUpWindow, self).__init__(content=NyAtmosphereLevelUpView(*args, **kwargs), layer=layer)
        self.__blurBackground = blurBackground
        self.__worldDrawEnabled = worldDrawEnabled
        self.__worldOn = False
        self.__blur = None
        self.onStatusChanged += self.__onStatusChanged
        return

    def isParamsEqual(self, *args, **kwargs):
        return self.__blurBackground == kwargs.get('blurBackground') and self.__worldDrawEnabled == kwargs.get('worldDrawEnabled')

    def _finalize(self):
        self.onStatusChanged -= self.__onStatusChanged
        if self.__worldOn and not self.__worldDrawEnabled and dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(True)
            AnimationSequence.setEnableAnimationSequenceUpdate(True)
        if self.__blur:
            self.__blur.fini()
            self.__blur = None
        super(NyLevelUpWindow, self)._finalize()
        return

    def __onStatusChanged(self, newState):
        if newState == WindowStatus.LOADED:
            self.__worldOn = dependency.instance(IHangarSpace).spaceInited and BigWorld.worldDrawEnabled()
            if self.__blurBackground:
                self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1, blurRadius=0.4)
            if self.__worldOn and not self.__worldDrawEnabled:
                BigWorld.worldDrawEnabled(False)
                AnimationSequence.setEnableAnimationSequenceUpdate(False)
