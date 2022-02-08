# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
import SoundGroups
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyBattlePassUrl
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_decorators import createTooltipContentDecorator, createBackportTooltipDecorator
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem, PackageType, ChapterStates
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar, showShop
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IBattlePassController
from skeletons.gui.shared import IItemsCache
WINDOW_IS_NOT_OPENED = -1
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}

class BattlePassBuyViewStates(object):

    def __init__(self):
        self.chapterID = WINDOW_IS_NOT_OPENED
        g_playerEvents.onDisconnected += self.reset
        g_playerEvents.onAccountBecomePlayer += self.reset

    def reset(self):
        self.chapterID = WINDOW_IS_NOT_OPENED

    def getPackageID(self):
        return self.chapterID


g_BPBuyViewStates = BattlePassBuyViewStates()
_logger = logging.getLogger(__name__)

class BattlePassBuyView(ViewImpl):
    __slots__ = ('__packages', '__selectedPackage', '__tooltipItems', '__backCallback', '__backBtnDescrLabel', '__tooltipWindow')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=BattlePassBuyViewModel, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        self.__backCallback = None if ctx is None else ctx.get('backCallback')
        self.__packages = {}
        self.__selectedPackage = None
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        super(BattlePassBuyView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassBuyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassBuyView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassBuyView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__packages = generatePackages(battlePass=self.__battlePassController)
        self.__setGeneralFields()
        self.__setPackages()
        if g_BPBuyViewStates.chapterID != WINDOW_IS_NOT_OPENED:
            self.__choosePackage({'packageID': g_BPBuyViewStates.getPackageID()})
        g_BPBuyViewStates.reset()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        super(BattlePassBuyView, self)._finalize()
        self.__removeListeners()
        self.__selectedPackage = None
        self.__tooltipItems = None
        self.__packages = None
        self.__tooltipWindow = None
        switchHangarOverlaySoundFilter(on=False)
        return

    def __setGeneralFields(self):
        with self.viewModel.transaction() as tx:
            tx.setIsWalletAvailable(self.__wallet.isAvailable)
            tx.setIsShopOfferAvailable(self.__isShopOfferAvailable())

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return

    def __onBackClick(self):
        if self.viewModel.getState() == self.viewModel.CONFIRM_STATE:
            self.__showBuy()
        elif self.__backCallback is not None:
            self.__backCallback()
        else:
            self.destroyWindow()
        return

    def __showConfirm(self):
        self.__setConfirmModel()
        self.viewModel.setState(self.viewModel.CONFIRM_STATE)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def __showBuy(self):
        self.__selectedPackage = None
        self.__clearTooltips()
        self.viewModel.setState(self.viewModel.BUY_STATE)
        return

    def __addListeners(self):
        model = self.viewModel
        model.choosePackage += self.__choosePackage
        model.showConfirm += self.__showConfirm
        model.showRewards += self.__showRewards
        model.onBackClick += self.__onBackClick
        model.onShopOfferClick += self.__onShopOfferClick
        model.confirm.onShowRewardsClick += self.__showRewards
        model.confirm.onBuyClick += self.__onBuyBattlePassClick
        self.__battlePassController.onLevelUp += self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange
        g_eventBus.addListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged

    def __removeListeners(self):
        model = self.viewModel
        model.choosePackage -= self.__choosePackage
        model.showConfirm -= self.__showConfirm
        model.showRewards -= self.__showRewards
        model.onBackClick -= self.__onBackClick
        model.onShopOfferClick -= self.__onShopOfferClick
        model.confirm.onShowRewardsClick -= self.__showRewards
        model.confirm.onBuyClick -= self.__onBuyBattlePassClick
        self.__battlePassController.onLevelUp -= self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange
        g_eventBus.removeListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged

    def __onBuying(self, _):
        self.__battlePassController.onLevelUp += self.__onLevelUp

    def __onAwardViewClose(self, _):
        self.destroyWindow()

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
        if self.viewModel.getState() == self.viewModel.CONFIRM_STATE:
            self.__setConfirmModel()
        elif self.viewModel.getState() == self.viewModel.BUY_STATE:
            self.__setPackages()
        elif self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateDetailRewards()
        else:
            self.__setPackages()

    def __choosePackage(self, args):
        packageID = int(args.get('packageID'))
        self.__selectedPackage = self.__packages[packageID]
        self.__showConfirm()

    def __setConfirmModel(self):
        if self.__selectedPackage is None:
            return
        else:
            self.__clearTooltips()
            self.viewModel.confirm.setPrice(self.__selectedPackage.getPrice())
            self.viewModel.confirm.setChapterID(self.__selectedPackage.getChapterID())
            isChapterActive = self.__selectedPackage.getChapterState() in (ChapterState.ACTIVE, ChapterState.COMPLETED)
            self.viewModel.confirm.setIsActive(isChapterActive)
            self.__updateDetailRewards()
            return

    def __updateDetailRewards(self):
        chapterID = self.__selectedPackage.getChapterID()
        fromLevel = 1
        toLevel = self.__selectedPackage.getCurrentLevel()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(chapterID)
            tx.setPackageState(PackageType.BATTLEPASS)
        packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), self.viewModel.rewards.futureRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self):
        if self.__selectedPackage is not None:
            self.__battlePassController.onLevelUp -= self.__onLevelUp
            BattlePassBuyer.buyBP(self.__selectedPackage.getSeasonID(), chapterID=self.__selectedPackage.getChapterID(), onBuyCallback=self.__onBuyBPCallback)
        return

    def __onBuyBPCallback(self, result):
        if not result:
            self.__battlePassController.onLevelUp += self.__onLevelUp
        else:
            self.__setPackages()
            self.__setGeneralFields()
            g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)

    def __isShopOfferAvailable(self):
        return not any((package.isBought() for package in self.__packages.itervalues()))

    def __onShopOfferClick(self):
        showShop(getBuyBattlePassUrl())
        self.destroyWindow()

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
            item.setChapterState(_CHAPTER_STATES.get(package.getChapterState()))
            item.setCurrentLevel(package.getCurrentLevel() + 1)
            model.packages.addViewModel(item)

        model.packages.invalidate()


class BattlePassBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(BattlePassBuyWindow, self).__init__(content=BattlePassBuyView(R.views.lobby.battle_pass.BattlePassBuyView(), wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, ctx=ctx), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
