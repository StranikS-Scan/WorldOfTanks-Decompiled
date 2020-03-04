# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_view.py
import logging
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_view_model import BattlePassBuyViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.battle_pass.battle_pass_helpers import isCurrentBattlePassStateBase, getFormattedTimeLeft
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_package import generatePackages
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.undefined_bonuses import isUndefinedBonusTooltipData, createUndefinedBonusTooltipWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from gui.sounds.filters import switchHangarOverlaySoundFilter
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IBattlePassController
from skeletons.gui.shared import IItemsCache
from battle_pass_common import BattlePassState
_logger = logging.getLogger(__name__)

class BattlePassBuyView(ViewImpl):
    __slots__ = ('__packages', '__selectedPackage', '__tooltipItems', '__backCallback', '__notifications', '__currentWaiting', '__tooltipWindow')
    __battlePassController = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, viewModelClazz=BattlePassBuyViewModel, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        self.__backCallback = None if ctx is None else ctx.get('backCallback')
        self.__packages = []
        self.__selectedPackage = None
        self.__tooltipItems = {}
        self.__currentWaiting = None
        self.__notifications = Notifiable()
        self.__tooltipWindow = None
        super(BattlePassBuyView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassBuyView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            isGFTooltip = isUndefinedBonusTooltipData(tooltipData)
            if isGFTooltip:
                window = createUndefinedBonusTooltipWindow(tooltipData, self.getParentWindow())
            else:
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            self.__tooltipWindow = window
            if window is None:
                return
            window.load()
            if isGFTooltip:
                window.move(event.mouse.positionX, event.mouse.positionY)
            return window
        else:
            return super(BattlePassBuyView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassBuyView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        with self.viewModel.transaction() as tx:
            tx.setIsBattlePassBought(self.__battlePassController.isBought())
            tx.setIsWalletAvailable(self.__wallet.isAvailable)
        self.__packages = generatePackages()
        self.__setPackages()
        switchHangarOverlaySoundFilter(on=True)
        self.__notifications.addNotificator(PeriodicNotifier(self.__timeTillUnlock, self.__updateUnlockTimes))

    def _finalize(self):
        super(BattlePassBuyView, self)._finalize()
        self.__removeListeners()
        self.__selectedPackage = None
        self.__tooltipItems = None
        self.__packages = None
        self.__tooltipWindow = None
        if self.__currentWaiting is not None:
            Waiting.hide(self.__currentWaiting)
            self.__currentWaiting = None
        switchHangarOverlaySoundFilter(on=False)
        self.__notifications.clearNotification()
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

    def __showConfirm(self):
        self.__setConfirmModel()
        self.viewModel.setState(self.viewModel.CONFIRM_STATE)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)

    def __showConfirmAny(self):
        self.__setConfirmAnyNumberModel()
        self.viewModel.setState(self.viewModel.CONFIRM_ANY_NUMBER_STATE)
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
        model.showConfirmAny += self.__showConfirmAny
        model.showRewards += self.__showRewards
        model.showBuy += self.__showBuy
        model.onBackClick += self.__onBackClick
        model.confirm.onShowRewardsClick += self.__showRewards
        model.confirm.onBuyClick += self.__onBuyBattlePassClick
        model.confirmAnyNumber.onChangeSelectedLevels += self.__onChangeSelectedLevels
        model.confirmAnyNumber.onBuyClick += self.__onBuyBattlePassClick
        model.confirmAnyNumber.onShowRewardsClick += self.__showRewards
        self.__battlePassController.onLevelUp += self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange
        self.__battlePassController.onUnlimitedPurchaseUnlocked += self.__updateState
        g_eventBus.addListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged += self.__onWalletChanged

    def __removeListeners(self):
        model = self.viewModel
        model.choosePackage -= self.__choosePackage
        model.showConfirm -= self.__showConfirm
        model.showConfirmAny -= self.__showConfirmAny
        model.showRewards -= self.__showRewards
        model.showBuy -= self.__showBuy
        model.onBackClick -= self.__onBackClick
        model.confirm.onShowRewardsClick -= self.__showRewards
        model.confirm.onBuyClick -= self.__onBuyBattlePassClick
        model.confirmAnyNumber.onChangeSelectedLevels -= self.__onChangeSelectedLevels
        model.confirmAnyNumber.onBuyClick -= self.__onBuyBattlePassClick
        model.confirmAnyNumber.onShowRewardsClick -= self.__showRewards
        self.__battlePassController.onLevelUp -= self.__onLevelUp
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange
        self.__battlePassController.onUnlimitedPurchaseUnlocked -= self.__updateState
        g_eventBus.removeListener(events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.__wallet.onWalletStatusChanged -= self.__onWalletChanged

    def __onBuying(self, _):
        self.__battlePassController.onLevelUp += self.__onLevelUp
        if self.__currentWaiting is not None:
            Waiting.hide(self.__currentWaiting)
        return

    def __onAwardViewClose(self, _):
        self.__onBackClick()

    def __onChangeSelectedLevels(self, args):
        self.__updateConfirmAnyNumberModel(args.get('count'))

    def __onLevelUp(self):
        self.__updateState()

    def __onSettingsChange(self, *_):
        if self.__battlePassController.isVisible() and not self.__battlePassController.isPaused():
            self.__updateState()
            self.__notifications.startNotification()
        else:
            showHangar()

    def __onWalletChanged(self, _):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)

    def __updateState(self):
        if self.viewModel.getState() == self.viewModel.CONFIRM_ANY_NUMBER_STATE:
            if self.__battlePassController.getState() == BattlePassState.POST:
                self.destroyWindow()
            self.__setConfirmAnyNumberModel()
        elif self.viewModel.getState() == self.viewModel.CONFIRM_STATE:
            self.__setConfirmModel()
        elif self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateDetailRewards()
        else:
            self.__setPackages()

    def __choosePackage(self, args):
        packageID = int(args.get('packageID'))
        self.__selectedPackage = self.__packages[packageID]
        if self.__selectedPackage.hasBattlePass():
            self.__showConfirm()
        else:
            self.__showConfirmAny()

    def __setConfirmModel(self):
        if self.__selectedPackage is None:
            return
        else:
            self.__clearTooltips()
            self.viewModel.confirm.setPrice(self.__selectedPackage.getPrice())
            self.viewModel.confirm.setLevelsCount(self.__selectedPackage.getLevelsCount())
            self.viewModel.confirm.setHasBattlePass(self.__selectedPackage.hasBattlePass())
            self.viewModel.confirm.setStartedProgression(self.__isStartedProgression())
            self.viewModel.confirm.setFinishedProgression(self.__isFinishedProgression())
            self.__updateDetailRewards()
            return

    def __setConfirmAnyNumberModel(self):
        if self.__selectedPackage is None:
            return
        else:
            with self.viewModel.confirmAnyNumber.transaction() as tx:
                tx.setLevelsTotal(self.__battlePassController.getMaxLevel())
                tx.setLevelsPassed(self.__battlePassController.getCurrentLevel())
            self.__updateConfirmAnyNumberModel(self.__selectedPackage.getLevelsCount())
            return

    def __updateConfirmAnyNumberModel(self, count):
        if self.__selectedPackage is None:
            return
        else:
            self.__selectedPackage.setLevels(int(count))
            self.__clearTooltips()
            with self.viewModel.confirmAnyNumber.transaction() as tx:
                tx.setAllowSlide(self.__selectedPackage.isDynamic())
                tx.setPrice(self.__selectedPackage.getPrice())
                tx.setLevelsSelected(self.__selectedPackage.getLevelsCount() + self.__battlePassController.getCurrentLevel())
                tx.rewards.clearItems()
                packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), tx.rewards, self.__tooltipItems)
            self.__updateDetailRewards()
            return

    def __updateDetailRewards(self):
        if not isCurrentBattlePassStateBase():
            curLevel = self.__battlePassController.getMaxLevel()
        else:
            curLevel = self.__battlePassController.getCurrentLevel()
        if self.__selectedPackage.hasBattlePass():
            fromLevel = 1
            toLevel = curLevel
        else:
            fromLevel = curLevel
            toLevel = curLevel + self.__selectedPackage.getLevelsCount()
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel + 1)
            tx.setToLevel(toLevel)
            tx.setStatePackage(self.__getTypePackage(self.__selectedPackage))
        packBonusModelAndTooltipData(self.__selectedPackage.getNowAwards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)
        packBonusModelAndTooltipData(self.__selectedPackage.getFutureAwards(), self.viewModel.rewards.futureRewards, self.__tooltipItems)

    def __onBuyBattlePassClick(self):
        if self.__selectedPackage is not None:
            self.__battlePassController.onLevelUp -= self.__onLevelUp
            if self.__selectedPackage.getLevelsCount() > 0:
                self.__currentWaiting = 'buyBattlePassLevels'
            else:
                self.__currentWaiting = 'buyBattlePass'
            Waiting.show(self.__currentWaiting)
            BattlePassBuyer.buy(self.__selectedPackage.getSeasonID(), self.__selectedPackage.getLevelsCount(), onBuyCallback=self.__onBuyCallback)
        return

    def __onBuyCallback(self, result):
        if not result:
            if self.__currentWaiting is not None:
                Waiting.hide(self.__currentWaiting)
            self.__battlePassController.onLevelUp += self.__onLevelUp
        else:
            g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        return

    def __isStartedProgression(self):
        return self.__battlePassController.getCurrentLevel() > 0

    def __isFinishedProgression(self):
        return self.__battlePassController.getState() != BattlePassState.BASE

    @replaceNoneKwargsModel
    def __setPackages(self, model=None):
        model.packages.clearItems()
        for packageID, package in enumerate(self.__packages):
            if not package.isVisible():
                continue
            item = PackageItem()
            item.setPackageID(packageID)
            item.setPrice(package.getPrice())
            item.setLevels(package.getLevelsCount())
            item.setIsBought(package.isBought())
            item.setType(self.__getTypePackage(package))
            item.setIsLocked(package.isLocked())
            self.__setPackageUnlockTime(item, package)
            model.packages.addViewModel(item)

        SoundGroups.g_instance.playSound2D(BattlePassSounds.getOverlay(model.packages.getItemsLength()))

    def __timeTillUnlock(self):
        minTime = 0
        for package in self.__packages:
            timeToUnlock = package.getTimeToUnlock()
            minTime = min(timeToUnlock, minTime) if minTime else timeToUnlock

        return minTime

    def __updateUnlockTimes(self):
        for packageModel, package in zip(self.viewModel.packages.getItems(), self.__packages):
            self.__setPackageUnlockTime(packageModel, package)

        self.viewModel.packages.invalidate()

    @staticmethod
    def __setPackageUnlockTime(model, package):
        timeToUnlock = package.getTimeToUnlock()
        model.setTimeToUnlock(getFormattedTimeLeft(timeToUnlock) if timeToUnlock else '')

    @staticmethod
    def __getTypePackage(package):
        if package.hasBattlePass():
            return PackageItem.BATTLE_PASS_TYPE
        return PackageItem.ANY_LEVELS_TYPE if package.isDynamic() else PackageItem.LIMITED_LEVELS_TYPE
