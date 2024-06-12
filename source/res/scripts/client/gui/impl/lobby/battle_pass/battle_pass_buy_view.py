# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
import SoundGroups
from constants import SECONDS_IN_THIRTY_DAYS
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyBattlePassUrl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import fillBattlePassCompoundPrice
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates, PackageItem, PackageType, ChapterType
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showHangar, showShop
from gui.shared.events import BattlePassEvent
from gui.shared.money import Currency
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
WINDOW_IS_NOT_OPENED = -1
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED,
 ChapterState.DISABLED: ChapterStates.DISABLED}
_CURRENCY_PRIORITY = (Currency.GOLD, Currency.FREE_XP)

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

class BattlePassBuyView(ViewImpl):
    __slots__ = ('__packages', '__selectedPackage', '__tooltipItems', '__backCallback', '__backBtnDescrLabel', '__tooltipWindow', '__packageID')
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassBuyView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattlePassBuyViewModel()
        self.__backCallback = None if ctx is None else ctx.get('backCallback')
        self.__packages = {}
        self.__selectedPackage = None
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        self.__packageID = None
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
        self.__packages = generatePackages(battlePass=self.__battlePass)
        self.__setGeneralFields()
        self.__setPackages()
        if g_BPBuyViewStates.chapterID != WINDOW_IS_NOT_OPENED:
            self.__choosePackage({'packageID': g_BPBuyViewStates.getPackageID()})
        g_BPBuyViewStates.reset()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        g_eventBus.removeListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        switchHangarOverlaySoundFilter(on=False)
        self.__selectedPackage = None
        self.__tooltipItems = None
        self.__packages = None
        self.__tooltipWindow = None
        super(BattlePassBuyView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.choosePackage, self.__choosePackage),
         (self.viewModel.showConfirm, self.__showConfirm),
         (self.viewModel.showRewards, self.__showRewards),
         (self.viewModel.onBackClick, self.__onBackClick),
         (self.viewModel.onShopOfferClick, self.__onShopOfferClick),
         (self.viewModel.confirm.onShowRewardsClick, self.__showRewards),
         (self.viewModel.confirm.onBuyClick, self.__onBuyBattlePassClick),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onMarathonChapterExpired, self.__onMarathonChapterExpired))

    def _getListeners(self):
        return ((BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY),)

    def __setGeneralFields(self):
        with self.viewModel.transaction() as tx:
            tx.setIsWalletAvailable(self.__wallet.isAvailable)
            tx.setIsShopOfferAvailable(self.__isShopOfferAvailable())
            tx.setShopOfferTimeLeft(self.__shopOfferTimeLeft())

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

    def __onBuying(self, _):
        self.__battlePass.onLevelUp += self.__onLevelUp

    def __onAwardViewClose(self, _):
        self.destroyWindow()

    def __onLevelUp(self):
        self.__updateState()

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
        self.__packageID = int(args.get('packageID'))
        self.__selectedPackage = self.__packages[self.__packageID]
        self.__showConfirm()

    @replaceNoneKwargsModel
    def __setConfirmModel(self, model=None):
        if self.__selectedPackage is None:
            return
        else:
            self.__clearTooltips()
            model.confirm.setPrice(self.__selectedPackage.getPrice())
            model.confirm.setChapterID(self.__selectedPackage.getChapterID())
            model.confirm.setIsActive(self.__selectedPackage.getChapterState() in (ChapterState.ACTIVE, ChapterState.COMPLETED))
            model.confirm.setCompoundPriceDefaultID(self.__getCompoundPriceDefaultID(self.__selectedPackage.getCompoundPrice()))
            fillBattlePassCompoundPrice(model.confirm.compoundPrice, self.__selectedPackage.getCompoundPrice())
            self.__updateDetailRewards()
            return

    def __updateDetailRewards(self):
        chapterID = self.__selectedPackage.getChapterID()
        fromLevel = 1
        toLevel = self.__selectedPackage.getCurrentLevel()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.topPriorityRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(chapterID)
            tx.setPackageState(PackageType.BATTLEPASS)
        packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), self.viewModel.rewards.futureRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getTopPriorityAwards(), self.viewModel.rewards.topPriorityRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self, ctx):
        if self.__selectedPackage is not None:
            self.__battlePass.onLevelUp -= self.__onLevelUp
            BattlePassBuyer.buyBP(self.__selectedPackage.getSeasonID(), self.__selectedPackage.getChapterID(), ctx.get('priceID'), self.__onBuyBPCallback)
        return

    def __onBuyBPCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp
        else:
            self.__setPackages()
            self.__setGeneralFields()
            g_eventBus.addListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)

    def __isShopOfferAvailable(self):
        return self.__battlePass.isShopOfferActive() and not any((package.isBought() and not package.isMarathon() for package in self.__packages.itervalues()))

    def __shopOfferTimeLeft(self):
        timeLeft = self.__battlePass.getShopOfferFinishTimeLeft()
        return timeLeft if timeLeft <= SECONDS_IN_THIRTY_DAYS else 0

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
            item.setChapterType(ChapterType(self.__battlePass.getChapterType(package.getChapterID())))
            item.setChapterState(_CHAPTER_STATES.get(package.getChapterState()))
            item.setCurrentLevel(package.getCurrentLevel() + 1)
            item.setExpireTime(self.__battlePass.getChapterRemainingTime(package.getChapterID()))
            fillBattlePassCompoundPrice(item.compoundPrice, package.getCompoundPrice())
            model.packages.addViewModel(item)

        model.packages.invalidate()

    def __getCompoundPriceDefaultID(self, compoundPrice):
        return next((priceID for currency in _CURRENCY_PRIORITY for priceID, priceData in compoundPrice.iteritems() if priceData.get(currency)))

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    def __onMarathonChapterExpired(self):
        self.__update()

    def __update(self):
        ctrl = self.__battlePass
        if ctrl.isPaused():
            showMissionsBattlePass()
            self.destroyWindow()
            return
        if not (ctrl.isEnabled() and ctrl.isActive()):
            showHangar()
            return
        if len(ctrl.getChapterIDs()) != self.viewModel.packages.getItemsLength():
            self.__packages = generatePackages(battlePass=ctrl)
            self.__setPackages()
        isValidState = not self.__packageID or ctrl.isChapterExists(self.__packageID) and (not ctrl.isMarathonChapter(self.__packageID) or ctrl.getChapterRemainingTime(self.__packageID) > 0)
        allBought = all((ctrl.isBought(chID) for chID in ctrl.getChapterIDs()))
        if not isValidState or allBought:
            showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
            self.destroyWindow()
            return
        self.__updateState()


class BattlePassBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(BattlePassBuyWindow, self).__init__(content=BattlePassBuyView(ctx=ctx), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
