# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/post_progression_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from battle_pass_common import FinalReward, BattlePassConsts, BattlePassTankmenSource
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import getReceivedTankmenCount, getTankmenShopPackages, getStyleForChapter, getVehicleInfoForChapter, isSeasonEndingSoon
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import ChapterStates
from gui.impl.gen.view_models.views.lobby.battle_pass.post_progression_view_model import PostProgressionViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared.event_dispatcher import showHangar, showVehiclePreviewWithoutBottomPanel, showBattlePassTankmenVoiceover, selectVehicleInHangar, showBattlePassBuyWindow, showStylePreview
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from web.web_client_api.common import ItemPackEntry, ItemPackType
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}

class PostProgressionView(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.PostProgressionView())
        settings.flags = ViewFlags.VIEW
        settings.model = PostProgressionViewModel()
        self.__chapter = None
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
        self.__battlePass.tankmenCacheUpdate()
        self.__chapter = self.__battlePass.getHolidayChapterID()
        self.__updateState()
        self.__fillModel()

    def _finalize(self):
        self.__chapter = None
        self.__tooltipItems = None
        super(PostProgressionView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),
         (self.viewModel.showRewards, self.__showRewards),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.viewModel.onPreviewVehicle, self.__onPreview),
         (self.viewModel.showVehicle, self.__showVehicle),
         (self.viewModel.showBuy, self.__showBuyWindow),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onEntitlementCacheUpdated, self.__updateState))

    def _getListeners(self):
        return ((events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),)

    def __fillModel(self):
        self.__setChapter()
        self.__updateDetailRewards()
        with self.viewModel.transaction() as model:
            model.setIsSpecialVoiceTankmen(not len(self.__battlePass.getSpecialTankmen()) < 2)
            model.setIsSeasonEndingSoon(isSeasonEndingSoon())
            self.__updateRewardChoice(model=model)

    def __setChapter(self):
        with self.viewModel.transaction() as tx:
            tx.setChapterID(self.__chapter)
            tx.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(self.__chapter)))
            tx.setCurrentLevel(self.__battlePass.getLevelInChapter(self.__chapter) + 1)

    def __isTankmenReceived(self, shopPackages):
        return all((packageCount - getReceivedTankmenCount(tankman) == 0 for tankman, packageCount in shopPackages.iteritems())) and all((getReceivedTankmenCount(tankman) > 0 for tankman, info in self.__battlePass.getSpecialTankmen().iteritems() if info.get('source') == BattlePassTankmenSource.QUEST_CHAIN)) and all((info.get('availableCount', 0) - getReceivedTankmenCount(tankman) == 0 for tankman, info in self.__battlePass.getSpecialTankmen().iteritems() if info.get('source') in BattlePassTankmenSource.PROGRESSION))

    def __update(self):
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
        elif not self.__battlePass.isActive():
            showHangar()
        else:
            self.__fillModel()
            self.__updateState()

    def __onBattlePassSettingsChanged(self, *_):
        self.__update()

    @replaceNoneKwargsModel
    def __updateRewardChoice(self, model=None):
        model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())

    def __updateDetailRewards(self):
        fromLevel = 1
        toLevel = self.__battlePass.getLevelInChapter(self.__chapter)
        with self.viewModel.rewards.transaction() as tx:
            tx.nowRewards.clearItems()
            tx.futureRewards.clearItems()
            tx.setFromLevel(fromLevel)
            tx.setToLevel(toLevel)
            tx.setChapterID(self.__chapter)
        packBonusModelAndTooltipData(self.__getRewards(), self.viewModel.rewards.nowRewards, self.__tooltipItems)

    def __getRewards(self):
        fromLevel = 1
        curLevel = self.__battlePass.getLevelInChapter(self.__chapter)
        bonuses = []
        if not self.__battlePass.isBought(self.__chapter):
            bonuses.extend(self.__battlePass.getPackedAwardsInterval(self.__chapter, fromLevel, curLevel, awardType=BattlePassConsts.REWARD_PAID))
        bonuses = BattlePassAwardsManager.uniteTokenBonuses(bonuses)
        return BattlePassAwardsManager.sortBonuses(bonuses)

    def __showRewards(self):
        self.viewModel.setState(self.viewModel.REWARDS_STATE)

    def __updateState(self):
        if not self.__battlePass.isBought(self.__chapter):
            state = self.viewModel.BUY_STATE
        elif not len(self.__battlePass.getSpecialTankmen()) < 2 and not self.__isTankmenReceived(getTankmenShopPackages()):
            state = self.viewModel.TANKMEN_STATE
        elif self.__battlePass.getNotChosenRewardCount() > 0:
            state = self.viewModel.SELECTABLE_REWARDS_STATE
        else:
            state = self.viewModel.FINAL_STATE
        self.viewModel.setState(state)

    def __onPreview(self):
        if FinalReward.STYLE in self.__battlePass.getPaidFinalRewardTypes(self.__chapter):
            styleInfo = getStyleForChapter(self.__chapter, battlePass=self.__battlePass)
            vehicleCD = getVehicleCDForStyle(styleInfo, itemsCache=self.__itemsCache)
            itemsPack = (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)
            showStylePreview(vehicleCD, style=styleInfo, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
             'tabIDs': (TabID.VEHICLE, TabID.STYLE),
             'currentTabID': TabID.STYLE,
             'style': styleInfo}, itemsPack=itemsPack, backCallback=showMissionsBattlePass)
        else:
            vehicle, style = getVehicleInfoForChapter(self.__chapter)
            if vehicle is not None:
                showVehiclePreviewWithoutBottomPanel(vehicle.intCD, style=style, backCallback=showMissionsBattlePass, isHeroInteractive=False)
        return

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    @staticmethod
    def __showTankmen():
        showBattlePassTankmenVoiceover()

    def __showVehicle(self):
        vehicle, _ = getVehicleInfoForChapter(self.__chapter)
        if vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD)
        else:
            showHangar()

    def __onAwardViewClose(self, *_):
        self.__updateState()
        self.__fillModel()

    @staticmethod
    def __showBuyWindow():
        showBattlePassBuyWindow()

    def __close(self):
        if self.viewModel.getState() == self.viewModel.REWARDS_STATE:
            self.__updateState()
        else:
            showHangar()
