# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_levels_view.py
import logging
import SoundGroups
from battle_pass_common import BattlePassState
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_decorators import createTooltipContentDecorator, createBackportTooltipDecorator
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_package import PackageAnyLevels
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IBattlePassController
from skeletons.gui.shared import IItemsCache
_rBattlePass = R.strings.battle_pass_2020
_logger = logging.getLogger(__name__)

class BattlePassBuyLevelView(ViewImpl):
    __slots__ = ('__package', '__tooltipItems', '__backCallback', '__backBtnDescrLabel', '__tooltipWindow', '__chapter')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=BattlePassBuyViewModel, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        self.__backCallback = None if ctx is None else ctx.get('backCallback')
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        self.__chapter = self.__battlePassController.getCurrentChapter()
        self.__package = PackageAnyLevels()
        super(BattlePassBuyLevelView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassBuyLevelView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassBuyLevelView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassBuyLevelView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
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
        super(BattlePassBuyLevelView, self)._finalize()
        self.__removeListeners()
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

    def __onBackClick(self):
        if self.__backCallback is not None:
            self.__backCallback()
        else:
            self.destroyWindow()
        return

    def __showConfirmAny(self):
        self.__setConfirmAnyNumberModel()
        self.viewModel.setState(self.viewModel.CONFIRM_ANY_NUMBER_STATE)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def __addListeners(self):
        model = self.viewModel
        model.onBackClick += self.__onBackClick
        model.showConfirmAny += self.__showConfirmAny
        model.confirmAnyNumber.onChangeSelectedLevels += self.__onChangeSelectedLevels
        model.confirmAnyNumber.onBuyClick += self.__onBuyBattlePassClick
        model.confirmAnyNumber.onShowRewardsClick += self.__showRewards
        self.__battlePassController.onLevelUp += self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange
        g_eventBus.addListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged

    def __removeListeners(self):
        model = self.viewModel
        model.onBackClick -= self.__onBackClick
        model.showConfirmAny -= self.__showConfirmAny
        model.confirmAnyNumber.onChangeSelectedLevels -= self.__onChangeSelectedLevels
        model.confirmAnyNumber.onBuyClick -= self.__onBuyBattlePassClick
        model.confirmAnyNumber.onShowRewardsClick -= self.__showRewards
        self.__battlePassController.onLevelUp -= self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange
        g_eventBus.removeListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged

    def __onBuying(self, _):
        self.__battlePassController.onLevelUp += self.__onLevelUp

    def __onAwardViewClose(self, _):
        self.__onBackClick()

    def __onChangeSelectedLevels(self, args):
        self.__updateConfirmAnyNumberModel(args.get('count'))

    def __onLevelUp(self):
        self.__updateState()

    def __onSettingsChange(self, *_):
        if self.__battlePassController.isVisible() and not self.__battlePassController.isPaused():
            self.__updateState()
        else:
            showHangar()

    def __onWalletChanged(self, _):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)

    def __updateState(self):
        if self.__isFinishedProgression() or self.__isChangedChapter():
            self.destroyWindow()
            return
        if self.viewModel.getState() == self.viewModel.CONFIRM_ANY_NUMBER_STATE:
            battlePassController, model = self.__battlePassController, self.viewModel
            levelsDelta = battlePassController.getCurrentLevel() - model.confirmAnyNumber.getLevelsPassed()
            packageLevelsCount = self.__package.getLevelsCount()
            if levelsDelta and packageLevelsCount > 1:
                self.__package.setLevels(packageLevelsCount - levelsDelta)
            self.__setConfirmAnyNumberModel()
        elif self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateDetailRewards()

    def __setConfirmAnyNumberModel(self):
        with self.viewModel.confirmAnyNumber.transaction() as tx:
            startLevel, endLevel = self.__battlePassController.getChapterLevelInterval(self.__chapter)
            tx.setLevelsTotal(endLevel)
            tx.setLevelsStart(startLevel - 1)
            tx.setChapter(self.__chapter)
            tx.setLevelsPassed(self.__battlePassController.getCurrentLevel())
        self.__updateConfirmAnyNumberModel(self.__package.getLevelsCount())

    def __updateConfirmAnyNumberModel(self, count):
        self.__package.setLevels(int(count))
        self.__clearTooltips()
        with self.viewModel.confirmAnyNumber.transaction() as tx:
            tx.setPrice(self.__package.getPrice())
            tx.setLevelsSelected(self.__package.getLevelsCount() + self.__battlePassController.getCurrentLevel())
            tx.rewards.clearItems()
            packBonusModelAndTooltipData(self.__package.getNowAwards(), tx.rewards, self.__tooltipItems)
        self.__updateDetailRewards()

    def __updateDetailRewards(self):
        curLevel = self.__battlePassController.getCurrentLevel()
        fromLevel = curLevel
        toLevel = curLevel + self.__package.getLevelsCount()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel + 1)
            tx.setToLevel(toLevel)
            tx.setStatePackage(PackageItem.ANY_LEVELS_TYPE)
            tx.setChapter(self.__chapter)
        packBonusModelAndTooltipData(self.__package.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self):
        self.__battlePassController.onLevelUp -= self.__onLevelUp
        BattlePassBuyer.buyLevels(self.__package.getSeasonID(), self.__package.getLevelsCount(), onBuyCallback=self.__onBuyLevelsCallback)

    def __onBuyLevelsCallback(self, result):
        if not result:
            self.__battlePassController.onLevelUp += self.__onLevelUp
        else:
            g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.ON_PURCHASE_LEVELS), scope=EVENT_BUS_SCOPE.LOBBY)

    def __isFinishedProgression(self):
        return self.__battlePassController.getState() == BattlePassState.COMPLETED

    def __isChangedChapter(self):
        return self.__chapter != self.__battlePassController.getCurrentChapter()


class BattlePassBuyLevelWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(BattlePassBuyLevelWindow, self).__init__(content=BattlePassBuyLevelView(R.views.lobby.battle_pass.BattlePassBuyView(), wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, ctx=ctx), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
