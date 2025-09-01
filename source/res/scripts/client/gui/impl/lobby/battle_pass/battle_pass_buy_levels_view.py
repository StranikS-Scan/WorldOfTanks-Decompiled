# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_levels_view.py
import logging
import SoundGroups
from battle_pass_common import BattlePassState
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_package import PackageAnyLevels
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_level_view_model import BattlePassBuyLevelViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageType
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showBattlePass
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
from skeletons.gui.shared import IItemsCache
_rBattlePass = R.strings.battle_pass
_logger = logging.getLogger(__name__)

class BuyLevelsPresenter(ViewComponent[BattlePassBuyLevelViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BuyLevelsPresenter, self).__init__(R.aliases.battle_pass.BuyLevels(), BattlePassBuyLevelViewModel)
        self.__backCallback = None
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        self.__chapterID = None
        self.__package = None
        self.updateInitialData(**kwargs)
        return

    @property
    def viewModel(self):
        return super(BuyLevelsPresenter, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def updateInitialData(self, **kwargs):
        self.__backCallback = kwargs.get('backCallback')
        newChapterID = kwargs.get('chapterID')
        if newChapterID is not None and (newChapterID != self.__chapterID or kwargs.get('reset', False)):
            self.__chapterID = newChapterID
            self.__package = PackageAnyLevels(self.__chapterID)
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)
        switchHangarOverlaySoundFilter(on=True)
        childStateID = kwargs.get('childStateID')
        if childStateID == R.aliases.battle_pass.BuyLevelsRewards():
            self.__showRewards()
        else:
            self.__showConfirmAny()
        return

    def activate(self):
        self.__battlePass.onLevelUp += self.__onLevelUp

    def deactivate(self):
        self.__battlePass.onLevelUp -= self.__onLevelUp
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)

    def onExtraChapterExpired(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            showBattlePass()

    def _onLoading(self, *args, **kwargs):
        super(BuyLevelsPresenter, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setIsWalletAvailable(self.__wallet.isAvailable)
            if self.__backCallback:
                backBtnText = backport.text(_rBattlePass.battlePassBuyLevelsView.backBtnText.shop())
            else:
                backBtnText = backport.text(_rBattlePass.battlePassBuyLevelsView.backBtnText.progression())
            tx.confirmAnyNumber.setBackBtnText(backBtnText)
        switchHangarOverlaySoundFilter(on=True)
        self.__showConfirmAny()

    def _finalize(self):
        super(BuyLevelsPresenter, self)._finalize()
        self.__clearTooltips()
        self.__tooltipItems = None
        self.__package = None
        self.__backCallback = None
        switchHangarOverlaySoundFilter(on=False)
        return

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return

    def __showConfirmAny(self):
        with self.viewModel.transaction() as model:
            self.__setConfirmAnyNumberModel(model=model.confirmAnyNumber)
            model.setState(model.CONFIRM_ANY_NUMBER_STATE)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def _getListeners(self):
        return ((events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.viewModel.showConfirmAny, self.__showConfirmAny),
         (self.viewModel.confirmAnyNumber.onChangeSelectedLevels, self.__onChangeSelectedLevels),
         (self.viewModel.confirmAnyNumber.onBuyClick, self.__onBuyBattlePassClick),
         (self.viewModel.confirmAnyNumber.onShowRewardsClick, self.__showRewards),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__battlePass.onBattlePassSettingsChange, self.__onSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onSettingsChanged),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged))

    def __onBuying(self, _):
        self.__battlePass.onLevelUp += self.__onLevelUp

    def __onAwardViewClose(self, _):
        showBattlePass(R.aliases.battle_pass.ChapterChoice() if self.__battlePass.isChapterCompleted(self.__chapterID) else R.invalid())

    def __onChangeSelectedLevels(self, args):
        self.__updateConfirmAnyNumberModel(args.get('count'))

    def __onLevelUp(self):
        self.__updateState()

    def __onSettingsChanged(self, *_):
        if self.__battlePass.isVisible():
            self.__updateState()

    def __onWalletChanged(self, _):
        with self.viewModel.transaction() as model:
            model.setIsWalletAvailable(self.__wallet.isAvailable)

    def __updateState(self):
        if self.__isFinishedProgression() or self.__isChapterCompleted():
            showBattlePass()
            return
        model = self.viewModel
        if model.getState() == model.CONFIRM_ANY_NUMBER_STATE:
            levelsDelta = self.__package.getCurrentLevel() - model.confirmAnyNumber.getLevelsPassed()
            packageLevelsCount = self.__package.getLevelsCount()
            if levelsDelta and packageLevelsCount > 1:
                self.__package.setLevels(packageLevelsCount - levelsDelta)
            with model.confirmAnyNumber.transaction() as tx:
                self.__setConfirmAnyNumberModel(tx)
        elif model.getState() == model.REWARDS_STATE:
            self.__updateDetailRewards()

    def __setConfirmAnyNumberModel(self, model):
        startLevel, endLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        model.setLevelsTotal(endLevel)
        model.setLevelsStart(startLevel - 1)
        model.setChapterID(self.__chapterID)
        model.setLevelsPassed(self.__package.getCurrentLevel())
        self.__updateConfirmAnyNumberModel(self.__package.getLevelsCount())

    def __updateConfirmAnyNumberModel(self, count):
        self.__package.setLevels(int(count))
        self.__clearTooltips()
        with self.viewModel.confirmAnyNumber.transaction() as tx:
            tx.setPrice(self.__package.getPrice())
            tx.setLevelsSelected(self.__package.getLevelsCount() + self.__package.getCurrentLevel())
            tx.rewards.clearItems()
            packBonusModelAndTooltipData(self.__package.getNowAwards(), tx.rewards, self.__tooltipItems)
        self.__updateDetailRewards()

    def __updateDetailRewards(self):
        curLevel = self.__package.getCurrentLevel()
        fromLevel = curLevel
        toLevel = curLevel + self.__package.getLevelsCount()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.setFromLevel(fromLevel + 1)
            tx.setToLevel(toLevel)
            tx.setPackageState(PackageType.ANYLEVELS)
            tx.setChapterID(self.__chapterID)
        packBonusModelAndTooltipData(self.__package.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self):
        self.__battlePass.onLevelUp -= self.__onLevelUp
        BattlePassBuyer.buyLevels(self.__package.getSeasonID(), self.__package.getChapterID(), self.__package.getLevelsCount(), onBuyCallback=self.__onBuyLevelsCallback)

    def __onBuyLevelsCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp
        else:
            g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.ON_PURCHASE_LEVELS), scope=EVENT_BUS_SCOPE.LOBBY)

    def __isFinishedProgression(self):
        return self.__battlePass.getState() == BattlePassState.COMPLETED

    def __isChapterCompleted(self):
        return self.__package.getChapterState() == ChapterState.COMPLETED
