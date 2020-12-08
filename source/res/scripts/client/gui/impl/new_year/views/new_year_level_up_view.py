# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_level_up_view.py
import random
from functools import partial
import BigWorld
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import SortedBonusNameQuestsBonusComposer
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, LootNewYearFragmentsPresenter, LootNewYearAlbumPresenter, LootNewYearToyPresenter, VehicleRewardPresenter, VehicleCompensationModelPresenter
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_level_up_view_model import NewYearLevelUpViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos, setOverlayHangarGeneral, PausedSoundManager
from gui.impl.lobby.missions.daily_quests_widget_view import predicateTooltipWindow
from gui.impl.new_year.new_year_helper import nyBonusSortOrder, IS_ROMAN_NUMBERS_ALLOWED, formatRomanNumber
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.new_year_tank_slot_tooltip import NewYearTankSlotTooltipContent
from gui.impl.new_year.tooltips.ny_talisman_tooltip import NewYearTalismanTooltipContent
from gui.impl.new_year.tooltips.toy_content import MegaToyContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyOverlay, LobbyNotificationWindow
from gui.server_events.awards_formatters import getNYAwardsPacker, AWARDS_SIZES
from gui.shared.event_dispatcher import showNewYearVehiclesView, showVideoView
from helpers import dependency, uniprof, isPlayerAccount
from items.components.ny_constants import CurrentNYConstants
from messenger.proto.events import g_messengerEvents
from shared_utils import findFirst, first
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ITalismanSceneController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_VEHICLES_BONUS_NAME = 'vehicles'
_MAX_CAPACITY = 6
_COMPENSATION_PRESENTERS = {_VEHICLES_BONUS_NAME: VehicleCompensationModelPresenter()}
_MODEL_PRESENTERS = {_VEHICLES_BONUS_NAME: VehicleRewardPresenter(),
 CurrentNYConstants.TOY_FRAGMENTS: LootNewYearFragmentsPresenter(),
 CurrentNYConstants.TOYS: LootNewYearToyPresenter(),
 'newYearAlbum': LootNewYearAlbumPresenter()}
_FIRST_LVL = 1

@loggerTarget(logKey=NY_LOG_KEYS.NY_TALISMANS, loggerCls=NYLogger)
class NewYearLevelUpWindowContent(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _talismanController = dependency.descriptor(ITalismanSceneController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_level_up_view.NewYearLevelUpView())
        settings.model = NewYearLevelUpViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearLevelUpWindowContent, self).__init__(settings)
        self.__tooltipData = {}
        self.__isFirstLevelUp = False
        self.__rewards = None
        self.__completedLevels = None
        self.__additionalRewards = None
        self.__spaceLoaded = False
        self.__cacheLoaded = False
        self.__callbackId = None
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        self.__vehicleBonus = None
        return

    @property
    def viewModel(self):
        return super(NewYearLevelUpWindowContent, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        if ctID == R.views.lobby.new_year.tooltips.ny_talisman_tooltip.NewYearTalismanTooltipContent():
            idx = int(event.getArgument('idx'))
            return NewYearTalismanTooltipContent(level=idx)
        if ctID == R.views.lobby.new_year.tooltips.new_year_tank_slot_tooltip.NewYearTankSlotTooltipContent():
            return NewYearTankSlotTooltipContent(level=self.viewModel.getLevel(), levelName=self.viewModel.getLevelName())
        if ctID == R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
            toyID = event.getArgument('toyID')
            return MegaToyContent(toyID)
        return super(NewYearLevelUpWindowContent, self).createToolTipContent(event, ctID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltipData[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NewYearLevelUpWindowContent, self).createToolTip(event)

    def hasRewards(self):
        return bool(self.__rewards)

    def appendRewards(self, ctx):
        for level, rewards in ctx.get('levelRewards', {}).iteritems():
            self.__rewards[level] = rewards
            self.__completedLevels.append(level)

        self.__completedLevels.sort()

    def _onLoading(self, ctx):
        super(NewYearLevelUpWindowContent, self)._onLoading()
        self.__rewards = ctx.get('levelRewards')
        self.__completedLevels = ctx.get('completedLevels')
        self.__additionalRewards = ctx.get('additionalRewards')
        self.__isFirstLevelUp = _FIRST_LVL in self.__rewards
        if self.__isFirstLevelUp:
            self.__saveVehicleData()
        self.__cacheLoaded = self._itemsCache.isSynced()
        self.__spaceLoaded = self._hangarSpace.spaceInited
        if self.__isFirstLevelUp and not (self.__spaceLoaded and self.__cacheLoaded):
            if not self.__cacheLoaded:
                self._itemsCache.onSyncCompleted += self.__onSyncCompleted
            if not self.__spaceLoaded:
                self._hangarSpace.onSpaceCreate += self.__onSpaceCreated
        else:
            self.__spaceLoaded = self.__cacheLoaded = True
            self.viewModel.setIsViewReady(True)
        self.viewModel.onClose += self.__onCloseAction
        self.viewModel.onToTanks += self.__onToTanks
        self.viewModel.onToTalismans += self.__onToTalismans
        self.__processNextReward()

    def __processNextReward(self):
        if self.__completedLevels:
            level = self.__completedLevels.pop(0)
            self.__setRewards(level, self.__rewards.pop(level), self.__additionalRewards)
            self.__additionalRewards = None
        return

    @loggerEntry
    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearLevelUpWindowContent, self)._initialize(*args, **kwargs)
        setOverlayHangarGeneral(True)

    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='exit')
    def _finalize(self):
        g_messengerEvents.onUnlockPopUpMessages()
        setOverlayHangarGeneral(False)
        super(NewYearLevelUpWindowContent, self)._finalize()
        self.__removeSyncHandler()
        self.__removeSpaceHandler()
        self.__rewards = None
        self.getViewModel().onClose -= self.__onCloseAction
        self.getViewModel().onToTanks -= self.__onToTanks
        self.getViewModel().onToTalismans -= self.__onToTalismans
        self._talismanController.onPreviewClosed -= self.__restoreWindow
        self.__videoStartStopHandler.onVideoDone()
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
        if self.__isFirstLevelUp:
            self.__processVehicleChange()
        return

    def __onCloseAction(self):
        if self.__completedLevels:
            self.__processNextReward()
            return
        if self.__isFirstLevelUp:
            windows = self.__gui.windowsManager.findWindows(predicateTooltipWindow)
            for window in windows:
                window.destroy()

            showVideoView(R.videos.lootboxes.ng_startup(), onVideoStarted=partial(self.__videoStartStopHandler.onVideoStart, videoId=LootBoxVideos.START), onVideoStopped=self.__onVideoDone, isAutoClose=True, soundControl=PausedSoundManager())
        else:
            self.destroyWindow()

    def __onVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        self.destroyWindow()

    def __onToTanks(self):
        if self.hasRewards():
            self.__hideWindow()
            showNewYearVehiclesView(backCtx=self.__restoreWindow)
        else:
            self.destroyWindow()
            showNewYearVehiclesView()

    @simpleLog(action=NY_LOG_ACTIONS.NY_TALISMAN_SELECT_FROM_REWARDS)
    def __onToTalismans(self):
        self._talismanController.switchToPreview()
        if self.hasRewards():
            self.__hideWindow()
            self._talismanController.onPreviewClosed += self.__restoreWindow
        else:
            self.destroyWindow()

    def __hideWindow(self):
        self.getParentWindow().hide()

    def __restoreWindow(self):
        self.getParentWindow().show()
        self.__processNextReward()

    def __setRewards(self, level, rewards, additionalRewards):
        hasTalisman = self._nyController.getLevel(level).hasTalisman()
        isLastLevel = self._nyController.getLevel(level).isLastLevel()
        allNotReceived = [ item.getSetting() for item in self._nyController.getTalismans() if not item.isInInventory() ]
        talismanSetting = random.choice(allNotReceived)
        with self.getViewModel().transaction() as model:
            model.setContainsTalisman(hasTalisman)
            model.setLevelName(formatRomanNumber(level))
            model.setTalismanSetting(talismanSetting)
            model.setHasVehicleBranch(self._nyController.getVehicleBranch().hasSlotWithLevel(level))
            model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            self.__fillRewardsList(rewardsList=model.getRewards(), rewards=self.__formatRewardsList(rewards, isLastLevel=isLastLevel))
            self.__fillRewardsList(rewardsList=model.getAdditionalRewards(), rewards=self.__formatRewardsList(additionalRewards))
            model.setLevel(level)

    def __fillRewardsList(self, rewardsList, rewards):
        rewardsList.clear()
        if rewards:
            for reward in rewards:
                formattedReward = self.__createRewardModel(reward)
                rewardsList.addViewModel(formattedReward)

        rewardsList.invalidate()

    def __createRewardModel(self, reward):
        tooltipId = len(self.__tooltipData)
        formatter = getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, _COMPENSATION_PRESENTERS)
        formattedReward = formatter.getModel(reward, tooltipId)
        self.__tooltipData[tooltipId] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))
        return formattedReward

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

    @classmethod
    def __formatRewardsList(cls, bonuses, isLastLevel=False):
        if not bonuses:
            return None
        else:
            formatter = SortedBonusNameQuestsBonusComposer(displayedAwardsCount=_MAX_CAPACITY if not isLastLevel else _MAX_CAPACITY - 1, awardsFormatter=getNYAwardsPacker(), sortFunction=nyBonusSortOrder)
            formattedBonuses = []
            if isLastLevel:
                albumBonus = {'bonusName': 'newYearAlbum'}
                formattedBonuses.append(albumBonus)
            formattedBonuses.extend(formatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG))
            return formattedBonuses

    def __removeSyncHandler(self):
        self._itemsCache.onSyncCompleted -= self.__onSyncCompleted

    def __removeSpaceHandler(self):
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreated

    def __onSpaceCreated(self):
        self.__removeSpaceHandler()
        self.__spaceLoaded = True
        self.__checkViewReady()

    def __onSyncCompleted(self, _, diff):
        self.__removeSyncHandler()
        self.__cacheLoaded = True
        self.__checkViewReady()

    def __checkViewReady(self):
        if self.__spaceLoaded and self.__cacheLoaded:
            self.setIsViewReadyAfterWheelFinish()

    def setIsViewReadyAfterWheelFinish(self):
        if Waiting.isVisible():
            self.__callbackId = BigWorld.callback(0.1, self.setIsViewReadyAfterWheelFinish)
        else:
            self.__callbackId = None
            self.viewModel.setIsViewReady(True)
        return


class NewYearLevelUpWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearLevelUpWindow, self).__init__(content=NewYearLevelUpWindowContent(*args, **kwargs))


class NewYearLevelUpWindowNWC(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearLevelUpWindowNWC, self).__init__(content=NewYearLevelUpWindowContent(*args, **kwargs))
