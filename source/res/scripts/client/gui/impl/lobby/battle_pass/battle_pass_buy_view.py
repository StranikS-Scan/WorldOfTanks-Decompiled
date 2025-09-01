# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
import SoundGroups
from PlayerEvents import g_playerEvents
from frameworks.wulf import Array
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_helpers import chaptersWithLogoBg, fillBattlePassCompoundPrice, getChapterType, getCompoundPriceDefaultID, isSeasonWithAdditionalBackground
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates, ChapterType, PackageItem, PackageType
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePass, showBuyBattlePassOverlay
from gui.shared.events import BattlePassEvent
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
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

class BuyPassPresenter(ViewComponent[BattlePassBuyViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, *args, **kwargs):
        super(BuyPassPresenter, self).__init__(R.aliases.battle_pass.BuyPass(), BattlePassBuyViewModel)
        self.__packages = {}
        self.__selectedPackage = None
        self.__tooltipItems = {}
        self.__tooltipWindow = None
        self.__packageID = kwargs.get('packageID', None)
        self.__selectedChapterID = self.__battlePass.getHolidayChapterID() if self.__battlePass.isHoliday() else kwargs.get('selectedChapterID')
        self.updateInitialData(**kwargs)
        return

    @property
    def viewModel(self):
        return super(BuyPassPresenter, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def updateInitialData(self, **kwargs):
        if 'packageID' in kwargs:
            self.__packageID = kwargs['packageID']
        childStateID = kwargs.get('childStateID')
        if childStateID == R.aliases.battle_pass.BuyPassConfirm():
            self.__choosePackage(self.__packageID)
        elif childStateID == R.aliases.battle_pass.BuyPassRewards():
            self.__showRewards()
        else:
            self.__showBuy()

    def onExtraChapterExpired(self):
        self.__update()

    def _onLoading(self, *args, **kwargs):
        super(BuyPassPresenter, self)._onLoading(*args, **kwargs)
        self.__packages = generatePackages(battlePass=self.__battlePass)
        self.__setGeneralFields()
        self.__setPackages()
        if self.__packageID is not None:
            self.__selectedPackage = self.__packages[self.__packageID]
            self.__setConfirmModel()
            self.__showConfirm()
        elif g_BPBuyViewStates.chapterID != WINDOW_IS_NOT_OPENED:
            self.__choosePackage(g_BPBuyViewStates.getPackageID())
        g_BPBuyViewStates.reset()
        return

    def _finalize(self):
        self.__selectedPackage = None
        self.__tooltipItems = None
        self.__packages = None
        self.__tooltipWindow = None
        super(BuyPassPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onShopOfferClick, self.__onShopOfferClick),
         (self.viewModel.confirm.onShowRewardsClick, self.__showRewards),
         (self.viewModel.confirm.onBuyClick, self.__onBuyBattlePassClick),
         (self.viewModel.confirm.onChangePurchaseWithLevels, self.__changeWithLevels),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onChapterChanged, self.__onChapterChanged))

    def _getListeners(self):
        return ((BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY), (BattlePassEvent.ON_FINISH_BATTLE_PASS_PURCHASE, self.__onFinishPurchase, EVENT_BUS_SCOPE.LOBBY))

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

    def __choosePackage(self, packageID):
        self.__packageID = int(packageID)
        self.__update()
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
            buyMethod = BattlePassBuyer.buyBP if not self.__selectedPackage.isWithLevels() else BattlePassBuyer.buyBPWithLevels
            buyMethod(self.__selectedPackage.getSeasonID(), self.__selectedPackage.getChapterID(), ctx.get('priceID'), self.__onBuyBPCallback)
        return

    def __onBuyBPCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp
        else:
            self.__setPackages()
            self.__setGeneralFields()

    def __isShopOfferAvailable(self):
        return not any((package.isBought() and not package.isExtra() and not package.isHoliday() for package in self.__packages.itervalues()))

    def __onShopOfferClick(self):
        showBuyBattlePassOverlay()

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

    def __onChapterChanged(self):
        self.__update(forceUpdatePackages=True)

    def __update(self, forceUpdatePackages=False):
        ctrl = self.__battlePass
        if forceUpdatePackages or len(ctrl.getMainChapterIDs()) != self.viewModel.packages.getItemsLength():
            self.__packages = generatePackages(battlePass=ctrl)
            self.__setPackages()
        isValidState = not self.__packageID or ctrl.isChapterExists(self.__packageID) and (not ctrl.isExtraChapter(self.__packageID) or ctrl.getChapterRemainingTime(self.__packageID) > 0)
        allBought = ctrl.isAllMainChaptersBought()
        if not isValidState or allBought:
            showBattlePass(R.aliases.battle_pass.ChapterChoice())
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
        showBattlePass(R.aliases.battle_pass.Progression())
