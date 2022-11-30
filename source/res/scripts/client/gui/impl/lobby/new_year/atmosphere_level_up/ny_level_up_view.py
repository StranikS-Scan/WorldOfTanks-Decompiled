# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/atmosphere_level_up/ny_level_up_view.py
import typing
import BigWorld
import AnimationSequence
import WebBrowser
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowLayer, ViewStatus, WindowStatus
from gui.Scaleform.Waiting import Waiting
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.atmosphere_level_up_model import AtmosphereLevelUpModel, ButtonActionType
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_guest_dog_token_tooltip import NyGuestDogTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_marketplace_token_tooltip import NyMarketplaceTokenTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import ADDITIONAL_BONUS_NAME_GETTERS, BLUEPRINT_NATION_ORDER, CREEBOOK_NATION_ORDER
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getSplitBonusFunction, VehiclesBonus
from gui.shared import event_dispatcher
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, uniprof, isPlayerAccount
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import NyATMReward, Ny23CoinToken
from messenger.proto.events import g_messengerEvents
from new_year.ny_constants import AnchorNames
from new_year.ny_navigation_helper import switchNewYearView
from new_year.ny_preview import getVehiclePreviewID
from shared_utils import findFirst, first
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
from uilogging.deprecated.decorators import loggerEntry
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.server_events.bonuses import SimpleBonus
    from gui.Scaleform.lobby_entry import LobbyEntry
_FIRST_LVL = 1
_MAX_HUGE_REWARDS = 4
_SHOW_HIDE_CONTAINERS = (WindowLayer.VIEW,)
_HIDE_DURATION = _SHOW_DURATION = 0.3
_HUGE_BONUSES = ('customizations_style',
 NyATMReward.DOG,
 'tmanToken',
 'vehicles',
 CREW_BOOK_RARITY.PERSONAL,
 CREW_BOOK_RARITY.UNIVERSAL)
_BONUSES_ORDER = (NyATMReward.DOG,
 NyATMReward.MARKETPLACE,
 'tmanToken',
 'customizations_style',
 'vehicles',
 'playerBadges',
 'singleAchievements') + CREEBOOK_NATION_ORDER + ('crewBooks', 'booster_credits', 'booster_xp') + BLUEPRINT_NATION_ORDER + ('BlueprintNationFragmentCongrats',
 Ny23CoinToken.TYPE,
 'booster_crew_xp',
 'BlueprintUniversalFragmentCongrats',
 'tankmen',
 'slots')
_BONUS_NAME_TO_BUTTON_ACTION = {NyATMReward.DOG: ButtonActionType.TOGUESTD,
 NyATMReward.MARKETPLACE: ButtonActionType.TOMARKERTPLACE,
 Ny23CoinToken.TYPE: ButtonActionType.TOGIFTMACHINE}
_ACTION_TO_ANCHOR = {ButtonActionType.TOEVENT: AnchorNames.UNDER_SPACE,
 ButtonActionType.TOGUESTD: AnchorNames.CELEBRITY_D,
 ButtonActionType.TOMARKERTPLACE: AnchorNames.MARKETPLACE,
 ButtonActionType.TOGIFTMACHINE: AnchorNames.GIFT_MACHINE}

def _customSplitBonuses(bonuses):
    split = []
    for bonus in bonuses:
        splitFunc = getSplitBonusFunction(bonus)
        if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
            split.extend(bonus.getVehiclesCrewBonuses())
            split.append(bonus)
        if splitFunc:
            split.extend(splitFunc(bonus))
        split.append(bonus)

    return split


def _splitHugeBonuses(bonuses):
    hugeBonuses = []
    otherBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(bonus)
        if bonusName in _HUGE_BONUSES:
            hugeBonuses.append(bonus)
        otherBonuses.append(bonus)

    if hugeBonuses:
        hugeBonuses.sort(key=_bonusesSortOrder)
        if len(hugeBonuses) > _MAX_HUGE_REWARDS:
            otherBonuses.extend(hugeBonuses[_MAX_HUGE_REWARDS:])
            hugeBonuses = hugeBonuses[:_MAX_HUGE_REWARDS]
    else:
        otherBonuses.sort(key=_bonusesSortOrder)
        delimiter = _MAX_HUGE_REWARDS if len(otherBonuses) >= _MAX_HUGE_REWARDS else len(otherBonuses)
        hugeBonuses.extend(otherBonuses[:delimiter])
        otherBonuses = otherBonuses[delimiter:]
    return (hugeBonuses, otherBonuses)


def _bonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)


class NyAtmosphereLevelUpView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gui = dependency.descriptor(IGuiLoader)
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.AtmosphereLevelUp())
        settings.model = AtmosphereLevelUpModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyAtmosphereLevelUpView, self).__init__(settings)
        self._tooltips = {}
        self.__isFirstLevelUp = False
        self.__rewards = {}
        self.__currentLevel = 0
        self.__completedLevels = []
        self.__callbackId = None
        self.__vehicleBonus = None
        self.__isLockEnabled = False
        return

    @property
    def viewModel(self):
        return super(NyAtmosphereLevelUpView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.tooltips.AdditionalRewardsTooltip() and self.viewStatus == ViewStatus.LOADED:
            showCount = int(event.getArgument('showedCount'))
            bonuses = _customSplitBonuses(self.__rewards[self.__currentLevel])
            _, secondaryBonuses = _splitHugeBonuses(bonuses)
            bonuses = sorted(secondaryBonuses, key=_bonusesSortOrder)[showCount:]
            bonusPackers = getNewYearBonusPacker()
            packedBonuses = []
            for bonus in bonuses:
                if bonus.isShowInGUI():
                    bonusList = bonusPackers.pack(bonus)
                    for item in bonusList:
                        packedBonuses.append(item)

            return AdditionalRewardsTooltip(packedBonuses)
        if ctID == R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip():
            return NyMarketplaceTokenTooltip()
        if ctID == R.views.lobby.new_year.tooltips.NyGuestDogTokenTooltip():
            return NyGuestDogTokenTooltip()
        return NyGiftMachineTokenTooltip() if ctID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip() else super(NyAtmosphereLevelUpView, self).createToolTipContent(event, ctID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyAtmosphereLevelUpView, self).createToolTip(event)

    def appendRewards(self, *_, **kwargs):
        for level, rewards in kwargs.get('levelRewards', {}).iteritems():
            self.__rewards[level] = rewards
            self.__completedLevels.append(level)

        self.__completedLevels.sort()

    def setIsViewReadyAfterWheelFinish(self):
        if Waiting.isVisible():
            self.__callbackId = BigWorld.callback(0.1, self.setIsViewReadyAfterWheelFinish)
        else:
            self.__callbackId = None
            self.viewModel.setIsViewReady(True)
        return

    def _getEvents(self):
        events = super(NyAtmosphereLevelUpView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAction, self.__onAction),
         (self.viewModel.onGoToHangar, self.__onGoToHangar),
         (self.viewModel.onStylePreview, self.__onStylePreview),
         (self.__nyController.onStateChanged, self.__onEventStateChanged))

    def _onLoading(self, *_, **kwargs):
        super(NyAtmosphereLevelUpView, self)._onLoading()
        self.__changeLayersVisibility(True)
        self.__isFirstLevelUp = _FIRST_LVL in self.__rewards
        if self.__isFirstLevelUp:
            self.__saveVehicleData()
            self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
            self.__hangarSpace.onSpaceCreate += self.__onSpaceCreated
            self.__checkViewReady()
        else:
            self.viewModel.setIsViewReady(True)
        self.__processNextReward()

    def __changeLayersVisibility(self, isHide):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(_SHOW_HIDE_CONTAINERS, time=_HIDE_DURATION)
            else:
                lobby.containerManager.showContainers(_SHOW_HIDE_CONTAINERS, time=_SHOW_DURATION)
        self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)

    @loggerEntry
    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NyAtmosphereLevelUpView, self)._initialize(*args, **kwargs)
        self.__switchLockers(True)

    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='exit')
    def _finalize(self):
        self.setHold(False)
        self.__switchLockers(False)
        super(NyAtmosphereLevelUpView, self)._finalize()
        self.__changeLayersVisibility(False)
        self.__removeSyncHandler()
        self.__rewards = None
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
        if self.__isFirstLevelUp and self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() > 0:
            self.__processVehicleChange()
        return

    def __hasRewards(self):
        return bool(set(self.__completedLevels).intersection(self.__rewards.keys()))

    def __processNextReward(self):
        if self.__completedLevels:
            self.__currentLevel = self.__completedLevels.pop(0)
            self.__setRewards()

    def __onClose(self):
        if self.__completedLevels:
            self.__processNextReward()
            return
        self.destroyWindow()

    def __onGoToHangar(self):
        if self.__completedLevels:
            self.__processNextReward()
            return
        event_dispatcher.showHangar()
        self.destroyWindow()

    def __onAction(self, args):
        action = args.get('actionType')
        if action is None:
            return
        else:
            actionType = ButtonActionType(action)
            anchor = _ACTION_TO_ANCHOR.get(actionType)
            if anchor:
                switchNewYearView(anchor)
                self.destroyWindow()
            return

    def __onStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            event_dispatcher.showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), showBackBtn=False, showCloseBtn=True)
            self.__onClose()
            return

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __setRewards(self):
        bonuses = self.__rewards[self.__currentLevel]
        bonuses = _customSplitBonuses(bonuses)
        hugeBonuses, otherBonuses = _splitHugeBonuses(bonuses)
        buttonAction = self.__getButtonAction(self.__currentLevel, bonuses)
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            self.__fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=_bonusesSortOrder, packer=getNewYearBonusPacker())
            self.__fillRewardsList(rewardsList=model.rewards.getItems(), bonuses=otherBonuses, sortMethod=_bonusesSortOrder, packer=getNewYearBonusPacker())
            model.setLevel(self.__currentLevel)
            model.setButtonAction(buttonAction)

    def __fillRewardsList(self, rewardsList, bonuses, sortMethod, packer):
        rewardsList.clear()
        bonuses.sort(key=sortMethod)
        packBonusModelAndTooltipData(bonuses, rewardsList, packer, self._tooltips)

    def __getBonusesNames(self, bonuses):
        names = []
        for b in bonuses:
            bonusName = b.getName()
            getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
            if getAdditionalName is not None:
                bonusName = getAdditionalName(b)
            names.append(bonusName)

        return names

    def __getButtonAction(self, level, bonuses):
        if level == _FIRST_LVL:
            return ButtonActionType.TOEVENT
        bonusesNames = self.__getBonusesNames(bonuses)
        for bonusName, action in _BONUS_NAME_TO_BUTTON_ACTION.iteritems():
            if bonusName in bonusesNames:
                return action

        return ButtonActionType.UNDEFINED

    def __saveVehicleData(self):
        vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', self.__rewards[_FIRST_LVL])
        if vehicleBonus is not None:
            self.__vehicleBonus = vehicleBonus
        return

    def __processVehicleChange(self):
        if not isPlayerAccount():
            return
        else:
            if self.__vehicleBonus is not None:
                vehicle, _ = first(self.__vehicleBonus.getVehicles(), (None, None))
                if vehicle is not None:
                    g_currentVehicle.selectVehicle(vehicle.invID)
            return

    def __removeSyncHandler(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreated

    def __onSpaceCreated(self):
        self.__checkViewReady()

    def __onSyncCompleted(self, _, diff):
        self.__checkViewReady()

    def __checkViewReady(self):
        if self.__itemsCache.isSynced() and self.__hangarSpace.spaceInited:
            self.__removeSyncHandler()
            self.setIsViewReadyAfterWheelFinish()

    def __switchLockers(self, enable):
        if self.__isLockEnabled == enable:
            return
        self.__isLockEnabled = enable
        if enable:
            g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True)
        else:
            g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)
        setOverlayHangarGeneral(enable)


class NyLevelUpWindow(LobbyNotificationWindow):
    __slots__ = ('__worldOn', '__blur')

    def __init__(self, *args, **kwargs):
        super(NyLevelUpWindow, self).__init__(content=NyAtmosphereLevelUpView(*args, **kwargs), layer=WindowLayer.OVERLAY)
        self.__worldOn = False
        self.onStatusChanged += self.__onStatusChanged
        self.__blur = None
        return

    def isParamsEqual(self, *args, **kwargs):
        return True

    def _initialize(self):
        super(NyLevelUpWindow, self)._initialize()
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)

    def _finalize(self):
        self.onStatusChanged -= self.__onStatusChanged
        if self.__worldOn and dependency.instance(IHangarSpace).spaceInited:
            AnimationSequence.setEnableAnimationSequenceUpdate(True)
            WebBrowser.pauseExternalCache(False)
        if self.__blur is not None:
            self.__blur.fini()
        super(NyLevelUpWindow, self)._finalize()
        return

    def __onStatusChanged(self, newState):
        if newState == WindowStatus.LOADED:
            self.__worldOn = dependency.instance(IHangarSpace).spaceInited and BigWorld.worldDrawEnabled()
            if self.__worldOn:
                AnimationSequence.setEnableAnimationSequenceUpdate(False)
                WebBrowser.pauseExternalCache(True)
