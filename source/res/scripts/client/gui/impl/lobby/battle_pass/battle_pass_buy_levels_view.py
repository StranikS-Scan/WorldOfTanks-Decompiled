# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_buy_levels_view.py
from __future__ import absolute_import
import logging
import SoundGroups
from frameworks.wulf import WindowLayer
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_buyer import BattlePassBuyer
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.battle_pass.battle_pass_package import PackageAnyLevels
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_level_view_model import BattlePassBuyLevelViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showBattlePass
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BuyLevelsPresenter(ViewComponent[BattlePassBuyLevelViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BuyLevelsPresenter, self).__init__(R.aliases.battle_pass.BuyLevels(), BattlePassBuyLevelViewModel)
        self.__tooltipItems = {}
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
        newChapterID = kwargs.get('chapterID')
        if newChapterID is not None and newChapterID != self.__chapterID:
            self.__chapterID = newChapterID
            self.__package = PackageAnyLevels(self.__chapterID)
        self.__fillModel()
        switchHangarOverlaySoundFilter(on=True)
        return

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self.__chapterID = None
        self.__package = None
        self.__clearTooltips()
        self._unsubscribe()
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        return

    def onExtraChapterExpired(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            showBattlePass()

    def _onLoading(self, *args, **kwargs):
        super(BuyLevelsPresenter, self)._onLoading(*args, **kwargs)
        self.__fillModel()
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.CONFIRM_BUY)

    def _finalize(self):
        super(BuyLevelsPresenter, self)._finalize()
        self.__clearTooltips()
        self.__tooltipItems = None
        self.__package = None
        switchHangarOverlaySoundFilter(on=False)
        return

    def _getListeners(self):
        return ((events.BattlePassEvent.BUYING_THINGS, self.__onBuying, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.viewModel.onPurchase, self.__onPurchase),
         (self.viewModel.onChangeSelectedLevels, self.__onChangeSelectedLevels),
         (self.__battlePass.onLevelUp, self.__onLevelUp),
         (self.__battlePass.onBattlePassSettingsChange, self.__onSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onSettingsChanged),
         (self.__wallet.onWalletStatusChanged, self.__onWalletChanged))

    def __clearTooltips(self):
        self.__tooltipItems.clear()

    @replaceNoneKwargsModel
    def __fillModel(self, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)
        _, endLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        model.setLevelsTotal(endLevel)
        model.setChapterID(self.__chapterID)
        model.setLevelsPassed(self.__package.getCurrentLevel())
        model.setLevelPrice(self.__package.getPrice())
        self.__clearTooltips()
        model.rewards.clearItems()
        packBonusModelAndTooltipData(self.__package.getNowAwards(), model.rewards, self.__tooltipItems)
        model.rewards.invalidate()

    def __onBuying(self, _):
        self.__battlePass.onLevelUp += self.__onLevelUp

    def __onAwardViewClose(self, _):
        if self.__battlePass.isChapterCompleted(self.__chapterID):
            if not self.__battlePass.isHoliday():
                showBattlePass(R.aliases.battle_pass.ChapterChoice())
        else:
            showBattlePass(R.invalid())

    def __onLevelUp(self):
        self.__updateState()

    def __onSettingsChanged(self, *_):
        if self.__battlePass.isVisible():
            self.__updateState()

    def __onWalletChanged(self, _):
        with self.viewModel.transaction() as model:
            model.setIsWalletAvailable(self.__wallet.isAvailable)

    def __updateState(self):
        if self.__battlePass.isCompleted() or self.__package.getChapterState() == ChapterState.COMPLETED:
            showBattlePass()
            return
        levelsDelta = self.__package.getCurrentLevel() - self.viewModel.getLevelsPassed()
        dynamicLevelsCount = self.__package.getDynamicLevelsCount()
        if levelsDelta and self.__package.getDynamicLevelsCount() > 1:
            self.__package.setLevels(dynamicLevelsCount - levelsDelta)
        with self.viewModel.transaction() as model:
            self.__fillModel(model=model)

    def __onPurchase(self):
        self.__battlePass.onLevelUp -= self.__onLevelUp
        BattlePassBuyer.buyLevels(self.__package.getSeasonID(), self.__package.getChapterID(), self.__package.getLevelsCount(), onBuyCallback=self.__onBuyLevelsCallback)

    @args2params(int)
    def __onChangeSelectedLevels(self, count):
        self.__package.setLevels(count)
        self.__clearTooltips()
        windows = self.gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOOLTIP)
        for window in windows:
            window.destroy()

        with self.viewModel.transaction() as model:
            model.rewards.clearItems()
            packBonusModelAndTooltipData(self.__package.getNowAwards(), model.rewards, self.__tooltipItems)
            model.rewards.invalidate()

    def __onBuyLevelsCallback(self, result):
        if not result:
            self.__battlePass.onLevelUp += self.__onLevelUp
        else:
            g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.ON_PURCHASE_LEVELS), scope=EVENT_BUS_SCOPE.LOBBY)
