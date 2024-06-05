# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
import SoundGroups
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, ViewStatus, Array
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import fillBattlePassCompoundPrice, getChapterType, getCompoundPriceDefaultID, isSeasonWithAdditionalBackground, chaptersWithLogoBg
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates, ChapterType, PackageItem, PackageType
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHangar, showBuyBattlePassOverlay
from gui.shared.events import BattlePassEvent
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
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

class BattlePassBuyView(ViewImpl):
    __slots__ = ('__packages', '__selectedPackage', '__tooltipItems', '__backCallback', '__backBtnDescrLabel', '__tooltipWindow', '__packageID')
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __gui = dependency.descriptor(IGuiLoader)

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
        if self.__battlePass.isHoliday():
            self.__selectedPackage = self.__packages[self.__battlePass.getHolidayChapterID()]
            self.__setConfirmModel()
            self.__showConfirm()
        elif g_BPBuyViewStates.chapterID != WINDOW_IS_NOT_OPENED:
            self.__choosePackage({'packageID': g_BPBuyViewStates.getPackageID()})
        g_BPBuyViewStates.reset()
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        g_eventBus.removeListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardCloseDuringPurchase, EVENT_BUS_SCOPE.LOBBY)
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
         (self.viewModel.confirm.onChangePurchaseWithLevels, self.__changeWithLevels),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onExtraChapterExpired, self.__onExtraChapterExpired))

    def _getListeners(self):
        return ((BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY), (BattlePassEvent.ON_FINISH_BATTLE_PASS_PURCHASE, self.__onFinishPurchase, EVENT_BUS_SCOPE.LOBBY), (events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, EVENT_BUS_SCOPE.LOBBY))

    def __setGeneralFields(self):
        with self.viewModel.transaction() as tx:
            tx.setIsWalletAvailable(self.__wallet.isAvailable)
            tx.setIsSeasonWithAdditionalBackground(isSeasonWithAdditionalBackground())
            tx.setIsShopOfferAvailable(self.__isShopOfferAvailable())
            chapterIDs = Array()
            for chapterID in chaptersWithLogoBg():
                chapterIDs.addNumber(chapterID)

            tx.setChaptersWithLogoBg(chapterIDs)

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return

    def __onBackClick(self):
        if not self.__battlePass.isHoliday() and self.viewModel.getState() == self.viewModel.CONFIRM_STATE:
            self.__showBuy()
        elif self.__backCallback is not None:
            self.__backCallback()
            self.destroyWindow()
        elif self.__isBattlePassOpen():
            if self.__battlePass.isHoliday() and self.__battlePass.isCompleted():
                showMissionsBattlePass(R.views.lobby.battle_pass.PostProgressionView())
            elif not self.__battlePass.getCurrentChapterID():
                showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
            self.destroyWindow()
        else:
            self.destroyWindow()
        return

    def __isBattlePassOpen(self):
        return self.__gui.windowsManager.findWindows(lambda w: w.content is not None and getattr(w.content, 'alias', None) == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS)

    def __onHeaderMenuClick(self, event):
        self.destroyWindow()

    def __showConfirm(self):
        if self.__selectedPackage is not None and self.viewModel.getState() != self.viewModel.REWARDS_STATE:
            self.__selectedPackage.resetWithLevels()
        self.__setConfirmModel()
        self.viewModel.setState(self.viewModel.CONFIRM_STATE)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)
        return

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
        elif self.viewModel.getState() == self.viewModel.BUY_STATE and not self.__battlePass.isHoliday():
            self.__setPackages()
        elif self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateDetailRewards()
        else:
            self.__setPackages()

    def __choosePackage(self, args):
        self.__packageID = int(args.get('packageID'))
        self.__selectedPackage = self.__packages[self.__packageID]
        self.__setPrevConfirmState()
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
            model.confirm.setCompoundPriceDefaultID(getCompoundPriceDefaultID(self.__selectedPackage.getCompoundPrice()))
            model.confirm.setIsPurchaseWithLevels(self.__selectedPackage.isWithLevels())
            model.confirm.setRemainingLevelsCount(self.__selectedPackage.getRemainingLevelsCount())
            fillBattlePassCompoundPrice(model.confirm.compoundPrice, self.__selectedPackage.getCompoundPrice())
            self.__updateDetailRewards(model=model)
            return

    @replaceNoneKwargsModel
    def __updateDetailRewards(self, model=None):
        chapterID = self.__selectedPackage.getChapterID()
        fromLevel, toLevel = self.__selectedPackage.getLevelsRange()
        with model.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.topPriorityRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(chapterID)
            tx.setPackageState(PackageType.BATTLEPASS)
            tx.setIsPurchaseWithLevels(self.__selectedPackage.isWithLevels())
        packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), model.rewards.nowRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), model.rewards.futureRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getTopPriorityAwards(), model.rewards.topPriorityRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self, ctx):
        if self.__selectedPackage is not None:
            self.__battlePass.onLevelUp -= self.__onLevelUp
            if not self.__selectedPackage.isWithLevels():
                buyMethod = BattlePassBuyer.buyBP
            else:
                buyMethod = BattlePassBuyer.buyBPWithLevels
            buyMethod(self.__selectedPackage.getSeasonID(), self.__selectedPackage.getChapterID(), ctx.get('priceID'), self.__onBuyBPCallback)
        return

    def __onBuyBPCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp
        else:
            self.__setPackages()
            self.__setGeneralFields()
            g_eventBus.addListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)

    def __isShopOfferAvailable(self):
        return not any((package.isBought() and not package.isExtra() and not package.isHoliday() for package in self.__packages.itervalues()))

    def __onShopOfferClick(self):
        showBuyBattlePassOverlay()
        g_eventBus.addListener(BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardCloseDuringPurchase, EVENT_BUS_SCOPE.LOBBY)

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
            item.setChapterType(ChapterType(getChapterType(package.getChapterID())))
            item.setChapterState(_CHAPTER_STATES.get(package.getChapterState()))
            item.setCurrentLevel(package.getCurrentLevel() + 1)
            item.setExpireTime(self.__battlePass.getChapterRemainingTime(package.getChapterID()))
            fillBattlePassCompoundPrice(item.compoundPrice, package.getCompoundPrice())
            model.packages.addViewModel(item)

        model.packages.invalidate()

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    def __onExtraChapterExpired(self):
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
        isValidState = not self.__packageID or ctrl.isChapterExists(self.__packageID) and (not ctrl.isExtraChapter(self.__packageID) or ctrl.getChapterRemainingTime(self.__packageID) > 0)
        allBought = all((ctrl.isBought(chID) for chID in ctrl.getChapterIDs()))
        if not isValidState or allBought:
            showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
            self.destroyWindow()
            return
        self.__updateState()

    @replaceNoneKwargsModel
    def __changeWithLevels(self, model=None):
        if model.getState() == self.viewModel.CONFIRM_STATE:
            self.__setPrevConfirmState()
            self.__selectedPackage.changeWithLevels()
            self.__setConfirmModel()

    @replaceNoneKwargsModel
    def __setPrevConfirmState(self, model=None):
        if self.__selectedPackage is not None:
            model.confirm.setPrevPrice(self.__selectedPackage.getPrice())
            model.rewards.prevTopPriorityRewards.clearItems()
            packBonusModelAndTooltipData(self.__selectedPackage.getTopPriorityAwards(), model.rewards.prevTopPriorityRewards, self.__tooltipItems)
        return

    def __onFinishPurchase(self, _):
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self.destroyWindow()

    def __onAwardCloseDuringPurchase(self, *_):
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED) and all((self.__battlePass.isBought(chapterID) for chapterID in self.__battlePass.getChapterIDs())):
            self.destroyWindow()


class BattlePassBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx, parent):
        super(BattlePassBuyWindow, self).__init__(content=BattlePassBuyView(ctx=ctx), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
