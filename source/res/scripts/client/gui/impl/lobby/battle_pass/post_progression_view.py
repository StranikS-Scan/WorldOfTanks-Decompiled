# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/post_progression_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import getSpecialVoiceTankmenInShop, getVehicleInfoForChapter
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.sounds import BATTLE_PASS_SOUND_SPACE
from gui.impl.gen import R
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem, ChapterStates, PackageType
from gui.impl.gen.view_models.views.lobby.battle_pass.post_progression_view_model import PostProgressionViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showHangar, showVehiclePreviewWithoutBottomPanel, showBattlePassTankmenVoiceover, selectVehicleInHangar, showBattlePassBuyWindow
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}

class PostProgressionView(ViewImpl):
    __slots__ = ('__packages', '__selectedPackage', '__tooltipItems')
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    _COMMON_SOUND_SPACE = BATTLE_PASS_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.PostProgressionView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = PostProgressionViewModel()
        self.__packages = {}
        self.__selectedPackage = None
        self.__tooltipItems = {}
        super(PostProgressionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PostProgressionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PostProgressionView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(PostProgressionView, self)._onLoading(*args, **kwargs)
        self.__packages = generatePackages(battlePass=self.__battlePass)
        self.__selectedPackage = self.__packages[self.__battlePass.getChapterIDs()[0]]
        self.__updateState()
        self._fillModel()
        self.__setStyleName()

    def _finalize(self):
        self.__selectedPackage = None
        self.__packages = None
        self.__tooltipItems = None
        super(PostProgressionView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),
         (self.viewModel.showRewards, self.__showRewards),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.viewModel.onPreviewVehicle, self.__onPreviewVehicle),
         (self.viewModel.showVehicle, self.__showVehicle),
         (self.viewModel.showBuy, self.__showBuyWindow),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged))

    def _getListeners(self):
        return ((events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),)

    def _fillModel(self):
        with self.viewModel.transaction() as model:
            self.__setPackages(model=model)
            self.__updateRewardChoice(model=model)
            self.__updateDetailRewards()

    @replaceNoneKwargsModel
    def __setPackages(self, model=None):
        model.packages.clearItems()
        for packageID, package in self.__packages.iteritems():
            if not package.isVisible():
                continue
            item = PackageItem()
            item.setPackageID(packageID)
            item.setPrice(package.getPrice())
            item.setIsBought(package.isBought())
            item.setType(PackageType.BATTLEPASS)
            item.setIsLocked(package.isLocked())
            item.setChapterID(package.getChapterID())
            item.setIsExtra(package.isExtra())
            item.setChapterState(_CHAPTER_STATES.get(package.getChapterState()))
            item.setCurrentLevel(package.getCurrentLevel() + 1)
            item.setExpireTime(self.__battlePass.getChapterRemainingTime(package.getChapterID()))
            model.packages.addViewModel(item)

        model.packages.invalidate()

    def __isTankmanRecieved(self):
        return all((self.__itemsCache.items.stats.entitlements.get(getRecruitInfo(tankman).getGroupName(), 0) > 0 for tankman in getSpecialVoiceTankmenInShop()))

    def __update(self):
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
        elif not self.__battlePass.isActive():
            showHangar()
        else:
            self._fillModel()
            self.__updateState()

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    def __updateDetailRewards(self):
        fromLevel = 1
        toLevel = self.__selectedPackage.getCurrentLevel()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(self.__selectedPackage.getChapterID())
            tx.setPackageState(PackageType.BATTLEPASS)
        packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), self.viewModel.rewards.futureRewards, self.__tooltipItems)

    def __setStyleName(self):
        _, style = getVehicleInfoForChapter(self.__battlePass.getChapterIDs()[0])
        with self.viewModel.transaction() as model:
            model.setStyleName(style.userName if style else '')

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def __updateState(self):
        if not self.__battlePass.isBought(self.__selectedPackage.getChapterID()):
            state = self.viewModel.BUY_STATE
        elif not self.__isTankmanRecieved():
            state = self.viewModel.TANKMEN_STATE
        elif self.__battlePass.getNotChosenRewardCount() > 0:
            state = self.viewModel.SELECTABLE_REWARDS_STATE
        else:
            state = self.viewModel.FINAL_STATE
        self.viewModel.setState(state)

    def __onPreviewVehicle(self):
        vehicle, style = getVehicleInfoForChapter(self.__selectedPackage.getChapterID())
        if vehicle is not None:
            showVehiclePreviewWithoutBottomPanel(vehicle.intCD, style=style, backCallback=showMissionsBattlePass, isHeroInteractive=False)
        return

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    @staticmethod
    def __showTankmen():
        showBattlePassTankmenVoiceover()

    def __showVehicle(self):
        vehicle, _ = getVehicleInfoForChapter(self.__selectedPackage.getChapterID())
        if vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD)
        else:
            showHangar()

    def __onAwardViewClose(self, *_):
        self.__updateState()
        self._fillModel()

    @staticmethod
    def __showBuyWindow():
        showBattlePassBuyWindow()

    def __close(self):
        if self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateState()
        else:
            showHangar()
