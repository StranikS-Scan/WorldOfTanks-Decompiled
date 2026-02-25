# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_package import generatePackage
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.buy_chapter_model import BuyChapterModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates, PackageType
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePass, showBuyBattlePassOverlay
from gui.shared.events import BattlePassEvent
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
_logger = logging.getLogger(__name__)
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}

class BuyPassPresenter(ViewComponent[BattlePassBuyViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, *args, **kwargs):
        super(BuyPassPresenter, self).__init__(R.aliases.battle_pass.BuyPass(), BattlePassBuyViewModel)
        self.__packageID = kwargs['chapterID']
        self.__selectedPackage = None
        self.__childStateID = kwargs.get('childStateID')
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        return

    @property
    def viewModel(self):
        return super(BuyPassPresenter, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def updateInitialData(self, **kwargs):
        if 'chapterID' in kwargs:
            chapter = kwargs['chapterID']
            if self.__packageID != chapter:
                self.__packageID = chapter
                self.__selectedPackage = generatePackage(self.__packageID)
        self.__childStateID = kwargs.get('childStateID')
        if self.__childStateID == R.aliases.battle_pass.BuyPassRewards():
            self.__showRewards()
        else:
            self.__showBuy()

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()
        self.__selectedPackage.resetWithLevels()
        self.viewModel.rewards.prevTopPriorityRewards.clearItems()
        self.__clearTooltips()

    def onExtraChapterExpired(self):
        if self.__battlePass.isExtraChapter(self.__packageID):
            showBattlePass()
            return
        self.__update()

    def _onLoading(self, *args, **kwargs):
        super(BuyPassPresenter, self)._onLoading(*args, **kwargs)
        self.__selectedPackage = generatePackage(self.__packageID, battlePass=self.__battlePass)
        if self.__childStateID == R.aliases.battle_pass.BuyPassRewards():
            self.viewModel.setState(self.viewModel.REWARDS_STATE)
        with self.viewModel.transaction() as model:
            self.__setGeneralFields(model=model)
            self.__setSelectedPackage(model=model)
            self.__setRegularChapters(model=model)

    def _finalize(self):
        self.__selectedPackage = None
        self.__tooltipItems = None
        self.__tooltipWindow = None
        super(BuyPassPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onShopOfferClick, self.__onShopOfferClick),
         (self.viewModel.onShowRewardsClick, self.__showRewards),
         (self.viewModel.onBuyClick, self.__onBuyBattlePassClick),
         (self.viewModel.onChangePurchaseWithLevels, self.__changeWithLevels),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged))

    def _getListeners(self):
        return ((BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY), (BattlePassEvent.ON_FINISH_BATTLE_PASS_PURCHASE, self.__onFinishPurchase, EVENT_BUS_SCOPE.LOBBY))

    @replaceNoneKwargsModel
    def __setGeneralFields(self, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)

    def __clearTooltips(self):
        self.__tooltipItems.clear()
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)
        self.__updateDetailRewards()

    def __showBuy(self):
        self.__clearTooltips()
        self.viewModel.setState(self.viewModel.BUY_STATE)
        self.__setSelectedPackage()

    def __onBuying(self, _):
        self.__battlePass.onLevelUp += self.__onLevelUp

    def __onLevelUp(self):
        self.__updateState()

    def __onWalletChanged(self, _):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)

    def __updateState(self):
        if self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateDetailRewards()
        else:
            self.__setSelectedPackage()

    @replaceNoneKwargsModel
    def __setSelectedPackage(self, model=None):
        model.setIsShopOfferAvailable(self.__isShopOfferAvailable())
        self.__clearTooltips()
        model.package.setPrice(self.__selectedPackage.getPrice())
        model.package.setChapterID(self.__selectedPackage.getChapterID())
        model.package.setIsActive(self.__selectedPackage.getChapterState() in (ChapterState.ACTIVE, ChapterState.COMPLETED))
        model.package.setIsPurchaseWithLevels(self.__selectedPackage.isWithLevels())
        model.package.setRemainingLevelsCount(self.__selectedPackage.getRemainingLevelsCount())
        model.package.starterPackRewards.clearItems()
        packBonusModelAndTooltipData(self.__battlePass.getChapterStarterPack(self.__packageID), model.package.starterPackRewards, self.__tooltipItems)
        model.package.starterPackRewards.invalidate()
        self.__updateDetailRewards(model=model)

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
            packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), tx.nowRewards, self.__tooltipItems)
            packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), tx.futureRewards, self.__tooltipItems)
            packBonusModelAndTooltipData(self.__selectedPackage.getTopPriorityAwards(), tx.topPriorityRewards, self.__tooltipItems)
            tx.nowRewards.invalidate()
            tx.futureRewards.invalidate()
            tx.topPriorityRewards.invalidate()

    def __onBuyBattlePassClick(self, *_):
        if self.__selectedPackage is not None:
            self.__battlePass.onLevelUp -= self.__onLevelUp
            buyMethod = BattlePassBuyer.buyBP if not self.__selectedPackage.isWithLevels() else BattlePassBuyer.buyBPWithLevels
            buyMethod(self.__selectedPackage.getSeasonID(), self.__selectedPackage.getChapterID(), self.__onBuyBPCallback)
        return

    def __onBuyBPCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp

    def __isShopOfferAvailable(self):
        return not self.__battlePass.isHoliday() and not self.__battlePass.isExtraChapter(self.__selectedPackage.getChapterID()) and not any((self.__battlePass.isBought(chapter) for chapter in self.__battlePass.getRegularChapterIDs()))

    def __onShopOfferClick(self):
        showBuyBattlePassOverlay()

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    def __update(self):
        ctrl = self.__battlePass
        isValidState = not self.__packageID or ctrl.isChapterExists(self.__packageID) and (not ctrl.isExtraChapter(self.__packageID) or ctrl.getChapterRemainingTime(self.__packageID) > 0)
        allBought = ctrl.isAllMainChaptersBought()
        if not isValidState or allBought:
            showBattlePass(R.aliases.battle_pass.ChapterChoice())
            return
        self.__selectedPackage = generatePackage(self.__packageID, battlePass=ctrl)
        self.__updateState()

    @replaceNoneKwargsModel
    def __changeWithLevels(self, model=None):
        self.__setPrevBuyState()
        self.__selectedPackage.changeWithLevels()
        self.__setSelectedPackage()

    @replaceNoneKwargsModel
    def __setPrevBuyState(self, model=None):
        if self.__selectedPackage is not None:
            model.package.setPrevPrice(self.__selectedPackage.getPrice())
            model.rewards.prevTopPriorityRewards.clearItems()
            packBonusModelAndTooltipData(self.__selectedPackage.getTopPriorityAwards(), model.rewards.prevTopPriorityRewards, self.__tooltipItems)
        return

    def __onFinishPurchase(self, _):
        showBattlePass(R.aliases.battle_pass.Progression(), self.__packageID)

    @replaceNoneKwargsModel
    def __setRegularChapters(self, model=None):
        chapters = model.getRegularChapters()
        chapters.clear()
        for chapterID in self.__battlePass.getRegularChapterIDs():
            chapterModel = BuyChapterModel()
            chapterModel.setChapterID(chapterID)
            chapterModel.setHasStarterPack(bool(self.__battlePass.getChapterStarterPack(chapterID)))
            chapters.addViewModel(chapterModel)

        chapters.invalidate()
