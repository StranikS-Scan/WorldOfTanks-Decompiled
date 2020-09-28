# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/postbattle_screen_view.py
import logging
import BigWorld
from constants import PremiumConfigs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.backport import createTooltipData, BackportTooltipWindow, BackportContextMenuWindow, createContextMenuData, text
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.postbattle.postbattle_screen_model import PostbattleScreenModel
from gui.impl.gen.view_models.views.lobby.postbattle.team_stats_model import TeamStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.lobby.postbattle.tooltips.exp_bonus import ExpBonusTooltip
from gui.impl.lobby.postbattle.tooltips.personal_efficiency import EfficiencyTooltip
from gui.impl.lobby.postbattle.tooltips.premium_plus import PremiumPlusTooltip
from gui.impl.lobby.postbattle.tooltips.progressive_reward import RewardsTooltip
from gui.impl.lobby.postbattle.tooltips.finance_details import FinancialTooltip
from gui.impl.pub import ViewImpl
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showTankPremiumAboutPage, showWtEventStorageBoxesWindow, showWtEventCollectionWindow
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.dossier.factories import getAchievementTooltipType
from gui.shared.utils.functions import makeTooltip
from gui.sounds.ambients import BattleResultsEnv
from gui.wt_event.wt_event_helpers import HUNTER_ELEMENT_NAME, BOSS_ELEMENT_NAME
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IGameSessionController, IGameEventController
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class PostbattleScreenView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__tooltipParametersCreator', '__tooltipContentCreator', '__tooltipItems')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __gameEventController = dependency.descriptor(IGameEventController)
    __sound_env__ = BattleResultsEnv

    def __init__(self, contentResID, ctx):
        settings = ViewSettings(contentResID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PostbattleScreenModel()
        super(PostbattleScreenView, self).__init__(settings)
        self.__arenaUniqueID = ctx.get('arenaUniqueID')
        if self.__arenaUniqueID is None:
            raise SoftException('Invalid arenaUniqueID.')
        self.__tooltipContentCreator = self.__getTooltipContentCreator()
        self.__tooltipParametersCreator = self.__getTooltipParametersCreator()
        self.__tooltipItems = {}
        return

    def getArenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(PostbattleScreenView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipID = event.getArgument('id')
            oldStyleTooltipId = event.getArgument('tooltipId')
            parametersCreator = self.__tooltipParametersCreator.get(tooltipID)
            tooltipData = self.__tooltipItems.get(oldStyleTooltipId)
            if parametersCreator is None and tooltipData is None:
                raise SoftException('Invalid arguments to create an old flash tooltip with id {}'.format(tooltipID))
            if parametersCreator:
                tooltipParameters = parametersCreator(event)
                window = BackportTooltipWindow(tooltipParameters, self.getParentWindow(), event)
            else:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
            window.load()
            return window
        else:
            return super(PostbattleScreenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipContentCreator = self.__tooltipContentCreator.get(contentID)
        if tooltipContentCreator is None:
            raise SoftException('Incorrect tooltip type with contentID {}'.format(contentID))
        return tooltipContentCreator(event)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            playerDbID = int(event.getArgument('dbID', 0))
            currentPlayer = BigWorld.player()
            if currentPlayer is None:
                raise SoftException('Player does not exist')
            if playerDbID == currentPlayer.databaseID:
                return
            team = event.getArgument('teamAlias', TeamStatsModel.ENEMIES_TEAM_ALIAS)
            args = {'dbID': playerDbID,
             'vehicleCD': event.getArgument('vehicleCD'),
             'isAlly': team == TeamStatsModel.ALLIES_TEAM_ALIAS,
             'arenaType': self.__battleResults.presenter.getArenaGuiType(self.__arenaUniqueID),
             'userName': event.getArgument('userName'),
             'clanAbbrev': event.getArgument('clanAbbrev')}
            window = BackportContextMenuWindow(createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, args), self.getParentWindow())
            window.load()
            return window
        else:
            return super(PostbattleScreenView, self).createContextMenu(event)

    def _onLoading(self, *args, **kwargs):
        super(PostbattleScreenView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__battleResults.presenter.setDataToModel(model, self.__arenaUniqueID, self.__tooltipItems)

    def _initialize(self, *args, **kwargs):
        super(PostbattleScreenView, self)._initialize(*args, **kwargs)
        self.__addListeners()
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        super(PostbattleScreenView, self)._finalize()
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.__removeListeners()
        self.__arenaUniqueID = None
        self.__tooltipParametersCreator = None
        self.__tooltipContentCreator = None
        self.__tooltipItems = None
        return

    def __addListeners(self):
        viewModel = self.viewModel
        viewModel.onChangeCurrentTab += self.__onChangeCurrentTab
        viewModel.common.rewards.onAppliedPremiumBonus += self.__onAppliedPremiumBonus
        viewModel.details.premiumBonuses.onBuyPremium += self.__onBuyPremiumPlus
        viewModel.onWidgetClick += self.__onWidgetClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChange
        self.__gameSession.onPremiumTypeChanged += self.__onPremiumStateChanged
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onUpdatePremiumBonus)
        g_clientUpdateManager.addCallbacks({'stats.applyAdditionalXPCount': self.__onUpdatePremiumBonus,
         'inventory': self.__onInventoryUpdated})

    def __removeListeners(self):
        viewModel = self.viewModel
        viewModel.onChangeCurrentTab -= self.__onChangeCurrentTab
        viewModel.common.rewards.onAppliedPremiumBonus -= self.__onAppliedPremiumBonus
        viewModel.details.premiumBonuses.onBuyPremium -= self.__onBuyPremiumPlus
        viewModel.onWidgetClick -= self.__onWidgetClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChange
        self.__gameSession.onPremiumTypeChanged -= self.__onPremiumStateChanged
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onUpdatePremiumBonus)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onChangeCurrentTab(self, args=None):
        tabId = args.get('tabId')
        if tabId is None:
            raise SoftException('Invalid arguments to extract an index of the tab')
        if tabId == PostbattleScreenModel.PERSONAL_TAB:
            self.__battleResults.presenter.updateTime(self.viewModel, self.__arenaUniqueID)
        return

    def __onAppliedPremiumBonus(self):
        self.__battleResults.applyAdditionalBonus(self.__arenaUniqueID)

    def __onSettingsChange(self, diff):
        premiumBonus = diff.get(PremiumConfigs.DAILY_BONUS)
        if premiumBonus is not None:
            self.__onUpdatePremiumBonus()
        return

    def __onInventoryUpdated(self, diff):
        if GUI_ITEM_TYPE.TANKMAN in diff or GUI_ITEM_TYPE.VEHICLE in diff:
            self.__onUpdatePremiumBonus()

    def __onUpdatePremiumBonus(self, _=None):
        with self.getViewModel().transaction() as model:
            self.__battleResults.presenter.updatePremiumBonus(model, self.__arenaUniqueID)

    def __onBuyPremiumPlus(self):
        showTankPremiumAboutPage()
        self.destroyWindow()

    def __onPremiumStateChanged(self, *_):
        with self.getViewModel().transaction() as model:
            self.__battleResults.presenter.updatePremiumState(model, self.__arenaUniqueID)

    def __onWidgetClick(self, args):
        widgetType = args.get('type')
        if widgetType is None:
            return
        else:
            if widgetType == 'ticket':
                self.__gameEventController.selectBoss()
            elif widgetType in (HUNTER_ELEMENT_NAME, BOSS_ELEMENT_NAME):
                showWtEventCollectionWindow()
            else:
                showWtEventStorageBoxesWindow()
            self.destroyWindow()
            return

    def __getTooltipContentCreator(self):
        return {R.views.lobby.postbattle.tooltips.ProgressiveReward(): self.__getProgressiveRewardTooltipContent,
         R.views.lobby.postbattle.tooltips.PersonalEfficiency(): self.__getPersonalEfficiencyTooltipContent,
         R.views.lobby.postbattle.tooltips.ExpBonus(): self.__getPremiumBonusTooltipContent,
         R.views.lobby.postbattle.tooltips.PremiumPlus(): self.__getPremiumPlusTooltipContent,
         R.views.lobby.postbattle.tooltips.FinanceDetails(): self.__getFinanceDetailsTooltipContent}

    def __getTooltipParametersCreator(self):
        return {AchievementModel.ACHIEVEMENT_TOOLTIP: self.__getAchievementTooltipParameters,
         DetailedPersonalEfficiencyModel.EFFICIENCY_PARAM_TOOLTIP: self.__getEfficiencyTooltipParameters,
         DetailedPersonalEfficiencyModel.EFFICIENCY_HEADER_PARAM_TOOLTIP: self.__getEfficiencyTooltipParameters,
         DetailedPersonalEfficiencyModel.TOTAL_EFFICIENCY_PARAM_TOOLTIP: self.__getTotalEfficiencyTooltipParameters,
         'widget': self.__getWidgetTooltipParameters}

    def __getAchievementTooltipParameters(self, event):
        achievementID = int(event.getArgument('achievementID'))
        achievementName = event.getArgument('achievementName')
        isPersonal = event.getArgument('isPersonal')
        args = self.__battleResults.presenter.getAchievementTooltipData(self.__arenaUniqueID, achievementID, achievementName, isPersonal)
        return createTooltipData(isSpecial=True, specialAlias=getAchievementTooltipType(achievementName), specialArgs=args)

    def __getEfficiencyTooltipParameters(self, event):
        parameterName = event.getArgument('type')
        enemyVehicleID = event.getArgument('vehicleID')
        args = [self.__battleResults.presenter.getEfficiencyTooltipData(self.__arenaUniqueID, parameterName, enemyVehicleID=enemyVehicleID)]
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EFFICIENCY_PARAM, specialArgs=args)

    def __getTotalEfficiencyTooltipParameters(self, event):
        args = [self.__battleResults.presenter.getTotalEfficiencyTooltipData(self.__arenaUniqueID, event.getArgument('type'))]
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TOTAL_EFFICIENCY_PARAM, specialArgs=args)

    def __getWidgetTooltipParameters(self, event):
        widgetType = event.getArgument('widgetType')
        if widgetType is None:
            raise SoftException('Missing widget type for the tooltip.')
        tooltip = ''
        alias = None
        specialArgs = []
        if widgetType == 'ticket':
            isWulfTooltip = True
            alias = TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET
        elif widgetType in ('wt_hunter', 'wt_boss', 'wt_special'):
            isWulfTooltip = True
            alias = TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX
            specialArgs = [widgetType]
        elif widgetType == 'hunter_collection':
            isWulfTooltip = False
            rCollection = R.strings.wt_event.bonuses.hunter_collection.tooltip
            tooltip = makeTooltip(text(rCollection.header()), text(rCollection.body()))
        elif widgetType == 'boss_collection':
            isWulfTooltip = False
            rCollection = R.strings.wt_event.bonuses.boss_collection.tooltip
            tooltip = makeTooltip(text(rCollection.header()), text(rCollection.body()))
        else:
            return
        return createTooltipData(tooltip=tooltip, isWulfTooltip=isWulfTooltip, specialAlias=alias, specialArgs=specialArgs)

    def __getPersonalEfficiencyTooltipContent(self, event):
        efficiencyType = event.getArgument('parameter')
        return EfficiencyTooltip(self.__arenaUniqueID, efficiencyType)

    def __getProgressiveRewardTooltipContent(self, _=None):
        sourceDataModel = self.viewModel.common.rewards.progressiveReward
        return RewardsTooltip(sourceDataModel)

    def __getPremiumBonusTooltipContent(self, _=None):
        sourceDataModel = self.viewModel.common.rewards.expBonus
        return ExpBonusTooltip(sourceDataModel)

    def __getPremiumPlusTooltipContent(self, _=None):
        return PremiumPlusTooltip()

    def __getFinanceDetailsTooltipContent(self, event):
        currencyType = event.getArgument('parameter')
        if currencyType is None:
            raise SoftException('Missing currency type for the tooltip.')
        return FinancialTooltip(self.__arenaUniqueID, currencyType)
