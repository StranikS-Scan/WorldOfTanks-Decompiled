# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_view.py
import SoundGroups
import typing
import CGF
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from gui.impl.gui_decorators import args2params
from gui.impl.pub import PopOverWindow
from new_year.gui.impl.lobby.new_year.ny_leaderboard_recount_view import NyLeaderboardRecountViewWindow
from new_year.gui.impl.lobby.new_year.pet.ny_pet_reward_view import PetRewardViewWindow
from new_year.gui.impl.lobby.new_year.pet.ny_pet_story_view import PetStoryViewWindow, PetStoryView
from new_year.helpers.ny_helpers import showWebmVideoView
from new_year.ny_constants import NY_HAS_PET_ANIMATION, NY_TAMAGOTCHI_STORY_TIP, NY_TAMAGOTCHI_SEEN_TIPS, NY_TAMAGOTCHI_STORY_BUBLE
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import ReturnPlace
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import IndicatorType
from new_year.gui.impl.lobby.new_year.env_switcher.ny_environment_switcher_controller import EnvironmentState
from new_year.gui.impl.lobby.new_year.popovers.ny_pet_item_activate_popover import NyPetItemActivatePopover
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_bonus_tooltip import NyPetBonusTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_indicator_tooltip import NyPetIndicatorTooltip
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.main_view_model import SwitchStates
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel, SingleTipType
from new_year.gui.impl.lobby.new_year.pet.ny_pet_indicators_block import NyPetIndicatorsBlock
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_mails_tooltip import NyPetMailsTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_token_stepper_tooltip import NyPetTokenStepperTooltip
from new_year.skeletons.new_year import IRaccoonAnimationController, INewYearCurrencyController, INewYearEnvironmentSwitchController, ITamagotchiDataProvider
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.lobby.new_year.pet.ny_pet_shop_view import NyPetShopView
from new_year.helpers.ny_fading_cover import NYFadingCover
from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
from new_year.helpers.server_settings import getNewYearGeneralConfig
from cgf_components.hangar_camera_manager import HangarCameraManager
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import InternalViewState
from new_year.tamagotchi.sys_msg.sys_msg_handler import TamagotchiSysMsgHandler
from skeletons.gui.game_control import IGuiLootBoxesController
from new_year.gui.impl.new_year.sounds import RaccoonStates, VideoStartStopHandler, Videos, NewYearSoundEvents
from gui.impl.common.fade_manager import FadeManager
from skeletons.gui.shared.utils import IHangarSpace
from new_year_account_settings import getNYSetting, setNYSettings
from frameworks.wulf import WindowLayer, WindowStatus
from helpers import dependency
from collections import deque
from functools import partial
from gui.impl.gen import R

class ProgressSequenceSteps(object):

    def __init__(self):
        super(ProgressSequenceSteps, self).__init__()
        self._steps = []

    def init(self):
        pass

    def fini(self):
        pass

    @property
    def _step(self):
        return self._steps and self._steps[0]

    def process(self, progress):
        item = self._step
        while item:
            stepProgress, handler = item
            if progress <= stepProgress:
                break
            handler()
            if self._steps:
                self._steps.popleft()
            item = self._step

    def setSteps(self, steps):
        self._steps = deque(steps)


class NyPetView(HistorySubModelPresenter):
    __slots__ = ('__shopView', '__indicatorsBlock', '__fadeManager', '__fadeSteps', '__videoHandler', '__petRewardWindow', '__indicatorFillActive', '__isFillSoundPlaying')
    _INTERNAL_VIEW_STATE = InternalViewState.RACCOON
    __raccoonCtrl = dependency.descriptor(IRaccoonAnimationController)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, viewModel=None, parentView=None, **kwargs):
        super(NyPetView, self).__init__(viewModel, parentView, **kwargs)
        self.__shopView = None
        self.__indicatorsBlock = None
        self.__fadeManager = None
        self.__fadeSteps = ProgressSequenceSteps()
        self.__videoHandler = None
        self.__petRewardWindow = None
        self.__indicatorFillActive = {IndicatorType.FOOD: False,
         IndicatorType.FUN: False,
         IndicatorType.ACTIVITY: False}
        self.__isFillSoundPlaying = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def hangarCameraManager(self):
        return CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)

    @property
    def __fadeStates(self):
        return ((0.85, self.__fadeManager.show), (0.97, partial(self.setInternalViewState, InternalViewState.RACCOON, True)), (0.99, partial(self.__nyEnvSwitcherController.switchEnvironment, EnvironmentState.RACCOON.value)))

    def initialize(self, isLoadedFromHangar, *args, **kwargs):
        self.__fadeManager = FadeManager(layer=WindowLayer.VIEW, coverFactory=NYFadingCover)
        self.__initRaccoonFlyState(isLoadedFromHangar)
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.MAIN)
        isOnboarding = self._dataProvider.isOnboarding
        with self.viewModel.transaction() as model:
            model.lootBox.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
            model.setIsGuiLootBoxesVisible(self.__guiLootBoxes.isEnabled())
            model.setIsOnboarding(isOnboarding)
            model.setHasPetAnimations(getNYSetting(NY_HAS_PET_ANIMATION))
            model.setIsOnboardingVideoClosed(not isOnboarding)
            model.setWasLeaderboardFinished(self._dataProvider.isLeaderboardFinished)
        if isOnboarding:
            TamagotchiSysMsgHandler.showSkipMsg()
            self.__showVideo()
        self.__indicatorsBlock = NyPetIndicatorsBlock(self.viewModel, self)
        self.__indicatorsBlock.initialize()
        self.__shopView = NyPetShopView(self.viewModel.shop, self)
        self.__shopView.initialize()
        self.__updateLootboxEntryPoint(self.__guiLootBoxes.getBoxesCount())
        self.__tryShowTip()
        self._dataProvider.onViewVisibilityChanged(True)
        super(NyPetView, self).initialize(*args, **kwargs)

    def finalize(self):
        super(NyPetView, self).finalize()
        self.__saveSeenTip()
        self.__clearPetRewardWindow()
        self.__forceStopFillSound()
        if self._dataProvider.isOnboarding:
            SoundGroups.g_instance.playSound2D(NewYearSoundEvents.OLDMAN_ONBOARDING_SKIP)
        self.__shopView.finalize()
        self.__indicatorsBlock.finalize()
        self.__fadeManager.destroy()
        self.__nyEnvSwitcherController.switchEnvironment(self.__nyEnvSwitcherController.userEnvState.value)
        self._dataProvider.onViewVisibilityChanged(False)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetIndicatorTooltip():
            indicatorType = self.__getIndicatorType(event)
            return NyPetIndicatorTooltip(NyPetIndicatorsBlock.getIndicator(indicatorType, self.viewModel))
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetMailsTooltip():
            return NyPetMailsTooltip()
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetBonusTooltip():
            return NyPetBonusTooltip(self.viewModel)
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetTokenStepperTooltip():
            indicatorType = self.__getIndicatorType(event)
            return NyPetTokenStepperTooltip(indicatorType)
        return super(NyPetView, self).createToolTipContent(event, contentID)

    def createPopOver(self, event):
        if event.contentID == R.views.new_year.lobby.new_year.popovers.NyPetItemActivatePopover():
            indicatorType = self.__getIndicatorType(event)
            content = NyPetItemActivatePopover(self.viewModel, NyPetIndicatorsBlock.getIndicator(indicatorType, self.viewModel), indicatorType)
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.load()
            return window
        return super(NyPetView, self).createPopOver(event)

    def _getEvents(self):
        result = ((self._nyController.onNySettingsChanged, self.__onNySettingsChanged),
         (self.__nyEnvSwitcherController.onEnvironmentSwitched, self.__onEnvironmentSwitched),
         (self.__guiLootBoxes.onBoxesCountChange, self.__updateLootboxEntryPoint),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__guiLootBoxes.onStatusChange, self.__onLootBoxesStatusChange),
         (self.viewModel.onLootBoxEntryPointClick, self.__onLootBoxEntryPointClick),
         (self.viewModel.onShopClick, self.__onShopClick),
         (self.viewModel.onGetGift, self.__onGetGift),
         (self.viewModel.onStoryClick, self.__onStoryClick),
         (self.viewModel.onOnboardingFinish, self.__onOnboardingFinish),
         (self.viewModel.onPetStateAnimationsChange, self.__onPetStateAnimationsChange),
         (self.viewModel.onDeleteItemLeaderboardPoint, self.__onDeleteItemLeaderboardPoint),
         (self.viewModel.onProgressFillSound, self.__onIndicatorFillSound),
         (self.viewModel.onCloseSingleTip, self.__onCloseSingleTip),
         (self._dataProvider.onOnboardingSkipped, self.__onOnboardingSkipped),
         (self._dataProvider.onUpdateTipsRequested, self.__onUpdateTipsRequested),
         (self._dataProvider.onItemsActivated, self.__onItemsActivated),
         (self._dataProvider.onItemsActivateRequested, self.__onItemsActivateRequested),
         (self._dataProvider.onGiftObtained, self.__onGiftObtained),
         (self._dataProvider.onSeasonEnded, self.__onSeasonEnded))
        if self.__hangarSpace.spaceID is not None and self.hangarCameraManager is not None:
            result += ((self.hangarCameraManager.onProgressChanged, self.__fadeSteps.process),)
        return result

    def __getIndicatorType(self, event):
        return IndicatorType(event.getArgument('type'))

    def __initRaccoonFlyState(self, isLoadedFromHangar):
        if not isLoadedFromHangar:
            NyPetView._INTERNAL_VIEW_STATE = InternalViewState.RACCOON
            self.__nyEnvSwitcherController.switchEnvironment(EnvironmentState.RACCOON.value)
            return
        self.setSwitchState(SwitchStates.WITH_SWITCHING_OBJS)
        self.__fadeSteps.setSteps(self.__fadeStates)
        NyPetView._INTERNAL_VIEW_STATE = InternalViewState.RACCOON_FLY

    def __onNySettingsChanged(self):
        config = getNewYearGeneralConfig()
        if config is not None and not config.getPetVisible():
            NewYearNavigation.closeMainView()
        return

    def __onEnvironmentSwitched(self):
        self.__fadeManager.hide()

    def __updateLootboxEntryPoint(self, count, *_):
        lastViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_COUNT)
        with self.viewModel.lootBox.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)

    def __onAvailabilityChange(self, *_):
        self.viewModel.lootBox.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())

    def __onLootBoxesStatusChange(self):
        self.viewModel.setIsGuiLootBoxesVisible(self.__guiLootBoxes.isEnabled())

    def __onLootBoxEntryPointClick(self, *_):
        showStorageView(returnPlace=ReturnPlace.TO_PET)

    def __onShopClick(self):
        self.__forceStopFillSound()
        self.__nyCurrencyController.setVisibleCurrencies(NyCurrencyType.CREDITS)
        self.__shopView.toggleVisibility(True)

    def __onGetGift(self):
        self.__forceStopFillSound()
        self.__petRewardWindow = PetRewardViewWindow(self.getParentWindow())
        self.__petRewardWindow.load()

    def __clearPetRewardWindow(self):
        if self.__petRewardWindow and self.__petRewardWindow.windowStatus not in (WindowStatus.DESTROYING, WindowStatus.DESTROYED):
            self.__petRewardWindow.destroy()
            self.__petRewardWindow = None
        return

    def __onStoryClick(self):
        self.__forceStopFillSound()
        PetStoryViewWindow(self.getParentWindow()).load()

    def __onOnboardingSkipped(self):
        SoundGroups.g_instance.playSound2D(NewYearSoundEvents.OLDMAN_ONBOARDING_SKIP)
        self.viewModel.setIsOnboarding(False)
        self._dataProvider.isOnboarding = False

    def __onGiftObtained(self, isSuccess, initialCount, count, isSecret, isRecalculation):
        if not isSuccess and isRecalculation:
            NyLeaderboardRecountViewWindow(parent=self.getParentWindow()).load()

    def __onItemsActivated(self, *_, **__):
        self.__tryShowTip()

    def __onItemsActivateRequested(self, *_, **__):
        if self._dataProvider.isOnboarding:
            SoundGroups.g_instance.playSound2D(NewYearSoundEvents.OLDMAN_ONBOARDING_SKIP)
            self._dataProvider.isOnboarding = False

    def __onUpdateTipsRequested(self, state):
        if state:
            self.__tryShowTip()
            return
        self.__saveSeenTip()

    def __tryShowTip(self):
        if self._dataProvider.isOnboarding:
            return
        pInfo = self._dataProvider.playerInfo
        seen = getNYSetting(NY_TAMAGOTCHI_SEEN_TIPS)
        if pInfo.indicators[IndicatorType.FUN.value] >= 0 and SingleTipType.FUNOPENED.value not in seen:
            self.viewModel.setSingleTip(SingleTipType.FUNOPENED)
            return
        if pInfo.indicators[IndicatorType.ACTIVITY.value] >= 0 and SingleTipType.ACTIVITYOPENED.value not in seen:
            self.viewModel.setSingleTip(SingleTipType.ACTIVITYOPENED)
            return
        if not self._dataProvider.isLeaderboardFinished and SingleTipType.LEADERBOARD.value not in seen:
            for name, points in pInfo.indicators.iteritems():
                lastLevel = self._dataProvider.config.indicators[name].levels[-1]
                if points >= lastLevel.points:
                    self.viewModel.setSingleTip(SingleTipType.LEADERBOARD)
                    return

        week = PetStoryView.getCurrentWeekStep()
        with self.viewModel.transaction() as tx:
            tx.setIsStoryEntryPointBubble(getNYSetting(NY_TAMAGOTCHI_STORY_BUBLE) != week)
            if getNYSetting(NY_TAMAGOTCHI_STORY_TIP) != week:
                tx.setSingleTip(SingleTipType.NEWSTORY)
                tx.setNewStoryOpenedNumber(week)
                return

    def __saveSeenTip(self):
        if self._dataProvider.isOnboarding:
            return
        with self.viewModel.transaction() as tx:
            tip = tx.getSingleTip()
            tx.setSingleTip(SingleTipType.EMPTY)
        if tip is SingleTipType.EMPTY:
            return
        if tip is SingleTipType.NEWSTORY:
            setNYSettings(NY_TAMAGOTCHI_STORY_TIP, PetStoryView.getCurrentWeekStep())
            return
        seen = getNYSetting(NY_TAMAGOTCHI_SEEN_TIPS)
        seen.add(tip.value)
        setNYSettings(NY_TAMAGOTCHI_SEEN_TIPS, seen)

    def __onOnboardingFinish(self):
        self.viewModel.setIsOnboarding(False)

    def __onPetStateAnimationsChange(self):
        with self.viewModel.transaction() as tx:
            desired = not tx.getHasPetAnimations()
            tx.setHasPetAnimations(desired)
        self.__raccoonCtrl.setAnimationsEnabled(desired)

    def __onSeasonEnded(self, _):
        if self._dataProvider.isLeaderboardFinished:
            self.viewModel.setWasLeaderboardFinished(True)
            if self.viewModel.getSingleTip() is SingleTipType.LEADERBOARD:
                self.viewModel.setSingleTip(SingleTipType.EMPTY)

    @args2params(IndicatorType, int)
    def __onDeleteItemLeaderboardPoint(self, type, id):
        array = NyPetIndicatorsBlock.getIndicator(type, self.viewModel).getItemLeaderboardPoint()
        for index, item in enumerate(array):
            if item.getId() == id:
                array.remove(index)
                array.invalidate()
                return

    def __showVideo(self):
        self.__videoHandler = VideoStartStopHandler(checkPauseOnStart=False)
        showWebmVideoView(videoSource=R.videos.new_year.pet.pet_story(), parent=self.getParentWindow(), onVideoStarted=self.__onVideoStarted, onVideoClosed=self.__onVideoClosed, isAutoClose=True, canEscape=True, isUIVisible=True, uiShowDelay=1)

    def __onVideoStarted(self):
        self.__videoHandler.onVideoStart(Videos.PET)

    def __onVideoClosed(self):
        self.__videoHandler.onVideoDone()
        self.__videoHandler = None
        self.viewModel.setIsOnboardingVideoClosed(True)
        return

    @args2params(IndicatorType, bool)
    def __onIndicatorFillSound(self, type, started):
        prevActive = self.__indicatorFillActive[type]
        if prevActive == started:
            return
        self.__indicatorFillActive[type] = started
        desiredPlaying = any(self.__indicatorFillActive.itervalues())
        if desiredPlaying != self.__isFillSoundPlaying:
            self.__playFillSound(desiredPlaying)
            self.__isFillSoundPlaying = desiredPlaying

    def __onCloseSingleTip(self):
        self.__saveSeenTip()
        self.__tryShowTip()

    def __forceStopFillSound(self):
        if self.__isFillSoundPlaying:
            self.__playFillSound(False)
            self.__isFillSoundPlaying = False
        for key in self.__indicatorFillActive.iterkeys():
            self.__indicatorFillActive[key] = False

    def __playFillSound(self, enable):
        soundEvent = RaccoonStates.PROGRESS_FILL_START if enable else RaccoonStates.PROGRESS_FILL_STOP
        SoundGroups.g_instance.playSound2D(soundEvent)
