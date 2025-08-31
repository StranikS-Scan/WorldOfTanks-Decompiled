# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/battle_result/wt_battle_result_view.py
import typing
import logging
import BigWorld
import ArenaType
from constants import PremiumConfigs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.backport import createTooltipData, BackportTooltipWindow, BackportContextMenuWindow, createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.postbattle.postbattle_screen_model import PostbattleScreenModel
from gui.impl.gen.view_models.views.lobby.postbattle.team_stats_model import TeamStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.lobby.postbattle.event import PostbattleScreenEventPlugin
from gui.impl.pub import ViewImpl
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showTankPremiumAboutPage
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.dossier.factories import getAchievementTooltipType
from gui.sounds.ambients import BattleResultsEnv
from gui.wt_event.wt_event_helpers import isWtEventBattleQuest
from helpers import dependency, time_utils
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IGameSessionController
from soft_exception import SoftException
from gui.Scaleform.Waiting import Waiting
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.Vehicle import getNationLessName
from constants import FINISH_REASON
from wt_battle_result_helpers import getPersonalTeamResult, isOwnSquad, isBot, isPlayerLeftBattle, getKillerID, setTeamStatsAchievements, isPersonalResults, createFieldsGetter, getAchievementTooltipData, EfficiencyItems, STAT_STUN_FIELD_NAMES, PersonalEfficiency, setBaseUserInfo, setBaseEnemyVehicleInfo, EfficiencyKeys
from constants import PREMIUM_TYPE
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_multi_params_model import EnemyMultiParamsModel
from gui.impl.gen.view_models.views.lobby.postbattle.efficiency_item_model import EfficiencyItemModel
from gui.shared.gui_items.Vehicle import getSimpleShortUserName, VEHICLE_CLASS_NAME
from gui.battle_results import reusable
from gui.impl.gen.view_models.views.lobby.postbattle.player_model import PlayerModel
from gui.server_events.events_helpers import EventInfoModel
from white_tiger_common.wt_constants import WT_TEAMS
from skeletons.gui.game_control import IQuestsController
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from white_tiger.gui.impl.lobby.wt_quests_view import HUNTER_QUEST_CHAINS, MAX_VISIBLE_QUESTS
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from skeletons.gui.server_events import IEventsCache
from white_tiger.gui.impl.lobby.packers.wt_event_quest_data_packer import WTEventBattleQuestUIDataPacker
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from white_tiger.gui.impl.lobby.battle_result.tooltips.personal_efficiency import WtEfficiencyTooltip
from white_tiger.gui.impl.lobby.battle_result.tooltips.exp_bonus import WtExpBonusTooltip
from white_tiger.gui.impl.lobby.battle_result.tooltips.finance_details import WtFinancialTooltip
from white_tiger.gui.impl.lobby.battle_result.tooltips.premium_plus import WtPremiumPlusTooltip
from white_tiger.gui.impl.lobby.battle_result.tooltips.progressive_reward import WtRewardsTooltip
from white_tiger.gui.battle_results.presenter.event import setWidgets
_logger = logging.getLogger(__name__)

def getDefaultParameterValue(player, parameterName):
    return getattr(player, EfficiencyItems[parameterName][EfficiencyKeys.ENEMY_PARAM_NAME], 0)


def getStunParameterValue(player, _=None):
    return player.stunNum


def getDamageParameterValue(player, _=None):
    return player.piercings


def getArmorParameterValue(player, _=None):
    return player.noDamageDirectHitsReceived + player.rickochetsReceived


def checkStunParameterValue(player, _=None):
    for stunParameter in STAT_STUN_FIELD_NAMES:
        value = getattr(player, stunParameter)
        if value > 0:
            return value


def checkStunIconShown(player, _=None):
    return player.stunNum > 0


def checkDamageIconShown(player, _=None):
    return player.damageDealt > 0


def checkArmorIconShown(player, _=None):
    return player.noDamageDirectHitsReceived or player.rickochetsReceived or player.damageBlockedByArmor


_PARAMETER_VALUE_CHECKER = {PersonalEfficiency.STUN: checkStunParameterValue}
_PARAMETER_VALUE_EXTRACTOR = {PersonalEfficiency.STUN: getStunParameterValue,
 PersonalEfficiency.DAMAGE: getDamageParameterValue,
 PersonalEfficiency.ARMOR: getArmorParameterValue}
_ICON_PARAMETER_CHECKER = {PersonalEfficiency.STUN: checkStunIconShown,
 PersonalEfficiency.DAMAGE: checkDamageIconShown,
 PersonalEfficiency.ARMOR: checkArmorIconShown}

class WtBattleResultView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__tooltipParametersCreator', '__tooltipContentCreator', '__eventPlugin', '__questBnsTooltipData', '__battleResultData', '__fieldsGetter', '__reusable', '__results')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __sound_env__ = BattleResultsEnv

    def __init__(self, contentResID, ctx):
        settings = ViewSettings(contentResID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PostbattleScreenModel()
        super(WtBattleResultView, self).__init__(settings)
        self.__arenaUniqueID = ctx.get('arenaUniqueID')
        if self.__arenaUniqueID is None:
            raise SoftException('Invalid arenaUniqueID.')
        vo = self.__battleResults.getResultsVO(self.__arenaUniqueID)
        self.__reusable = None
        reusableRaw = vo.get('reusable')
        if reusableRaw:
            self.__reusable = reusable.createReusableInfo(reusableRaw)
        self.__results = vo.get('results')
        self.__eventPlugin = PostbattleScreenEventPlugin(self)
        self.__tooltipContentCreator = self.__getTooltipContentCreator()
        self.__tooltipParametersCreator = self.__getTooltipParametersCreator()
        self.__questBnsTooltipData = {}
        self.__fieldsGetter = None
        return

    @property
    def viewModel(self):
        return super(WtBattleResultView, self).getViewModel()

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipParameters = self.__getTooltipParameters(event)
            window = BackportTooltipWindow(tooltipParameters, self.getParentWindow())
            window.load()
            return window
        return super(WtBattleResultView, self).createToolTip(event)

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
             'arenaType': self.__reusable.common.arenaGuiType,
             'userName': event.getArgument('userName'),
             'clanAbbrev': event.getArgument('clanAbbrev')}
            window = BackportContextMenuWindow(createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, args), self.getParentWindow())
            window.load()
            return window
        else:
            return super(WtBattleResultView, self).createContextMenu(event)

    def _onLoading(self, *args, **kwargs):
        super(WtBattleResultView, self)._onLoading(*args, **kwargs)
        if self.__battleResults.areResultsPosted(self.__arenaUniqueID):
            with self.getViewModel().transaction() as model:
                self.__setDataModel(model)
        else:
            Waiting.show('stats')
            self.__battleResults.onResultPosted += self.__handleBattleResultsPosted

    def __setDataModel(self, model):
        if self.__reusable is None or self.__results is None:
            return
        else:
            self.__setPersonalData(model.common)
            self.__setUserStatus(model.userStatus)
            self.__setTeamStatsData(model.team)
            self.__setEventsData(model.events, self.__questBnsTooltipData)
            setWidgets(model.widgets, self.__reusable)
            return

    def __setPersonalData(self, model):
        self.__setGeneralInfoData(model.generalInfo)
        self.__setRewards(model.rewards)
        self.__setDetailedEfficiency(model.detailedEfficiency)

    def __setUserStatus(self, model):
        playerId = self.__reusable.getPlayerInfo().dbID
        vehicleId = self.__reusable.vehicles.getVehicleID(playerId)
        vehicleInfo = self.__reusable.vehicles.getVehicleInfo(vehicleId)
        setBaseUserInfo(model.user, vehicleId, self.__reusable)
        killerVehicleID = getKillerID(self.__results, vehicleInfo.intCD)
        if killerVehicleID:
            setBaseUserInfo(model.killer.user, killerVehicleID, self.__reusable)
            isPersonal = killerVehicleID == vehicleId
            model.killer.setIsPersonal(isPersonal)
            model.killer.setIsSameSquad(isOwnSquad(self.__reusable, killerVehicleID) and not isPersonal)
            killerInfo = self.__reusable.getPlayerInfoByVehicleID(killerVehicleID)
            model.killer.setIsBot(isBot(killerInfo))
        model.setIsLeftBattle(isPlayerLeftBattle(self.__reusable))
        model.setAttackReason(vehicleInfo.deathReason)

    def __setGeneralInfoData(self, model):
        winStatus = getPersonalTeamResult(self.__reusable)
        model.setWinStatus(winStatus)
        arenaGuiType = self.__reusable.common.arenaGuiType
        battleType = R.strings.menu.loading.battleTypes.num(arenaGuiType)()
        model.setBattleType(battleType)
        arenaType = ArenaType.g_cache[self.__reusable.common.arenaTypeID]
        model.setArenaName(arenaType.geometryName)
        playerInfo = self.__reusable.getPlayerInfo()
        playerId = playerInfo.dbID
        vehicleId = self.__reusable.vehicles.getVehicleID(playerId)
        vehicleInfo = self.__reusable.vehicles.getVehicleInfo(vehicleId)
        vehicle = self.__itemsCache.items.getItemByCD(vehicleInfo.intCD)
        noNationName = getNationLessName(vehicle.name)
        vehicleIconName = replaceHyphenToUnderscore(noNationName)
        model.setVehicleIconName(vehicleIconName)
        model.setVehicleLevel(vehicle.level)
        model.setVehicleType(vehicle.type)
        model.setLocalizedVehicleName(vehicle.userName)
        if self.__reusable.common.finishReason != FINISH_REASON.TECHNICAL:
            model.setBattleFinishReason(self.__reusable.common.finishReason)
        common = self.__results['common']
        finishTime = common.get('arenaCreateTime', 0) + common.get('duration', 0)
        model.setBattleFinishTime(finishTime)
        model.setServerTime(time_utils.getServerUTCTime())

    def __setRewards(self, model):
        avatarInfo = self.__results['personal']['avatar']
        model.setCredits(avatarInfo['credits'])
        model.setExperience(avatarInfo['xp'])
        model.setCrystals(avatarInfo['crystal'])
        achievements = Array()
        left, right = self.__reusable.personal.getAchievements(self.__results)
        for achievement in [left, right]:
            if not achievement:
                continue
            achievementModel = AchievementModel()
            achievementModel.setName(achievement.name)
            achievementModel.setIsEpic(achievement.isEpic)
            achievementModel.setIconName(achievement.iconName)
            achievementModel.setGroupID(achievement.groupID)
            achievementModel.setAchievementID(achievement.achievementID)
            achievementModel.setIsPersonal(achievement.isPersonal)
            achievements.addViewModel(achievementModel)

        model.setAchievements(achievements)

    def __setDetailedEfficiency(self, model):
        isPrematureLeave = self.__reusable.personal.avatar.isPrematureLeave
        hasPenalties = self.__reusable.personal.avatar.hasPenalties()
        if isPrematureLeave or hasPenalties:
            return
        enemyItems = Array()
        enemies = []
        for _, enemies in self.__reusable.getPersonalDetailsIterator(self.__results['personal']):
            continue

        for enemy in enemies:
            hasParams = False
            for param in PersonalEfficiency.ALL:
                checker = _PARAMETER_VALUE_CHECKER.get(param, getDefaultParameterValue)
                if checker(enemy, param) > 0:
                    hasParams = True
                    continue

            if not hasParams:
                continue
            enemyItem = EnemyMultiParamsModel()
            setBaseUserInfo(enemyItem.user, enemy.vehicleID, self.__reusable)
            enemyItem.setDbID(enemy.player.dbID)
            setBaseEnemyVehicleInfo(enemyItem, enemy)
            enemyItem.setVehicleCD(enemy.vehicle.intCD)
            enemyItem.setVehicleID(enemy.vehicleID)
            enemyItemParams = enemyItem.getParams()
            for paramName in PersonalEfficiency.ALL:
                paramItem = EfficiencyItemModel()
                paramItem.setParamName(paramName)
                totalExtractor = _PARAMETER_VALUE_EXTRACTOR.get(paramName, getDefaultParameterValue)
                paramItem.setSimpleValue(totalExtractor(enemy, paramName))
                iconChecker = _ICON_PARAMETER_CHECKER.get(paramName, getDefaultParameterValue)
                paramItem.setIsVisible(iconChecker(enemy, paramName))
                paramItem.setDetailedValue(getDefaultParameterValue(enemy, paramName))
                enemyItemParams.addViewModel(paramItem)

            enemyItemParams.invalidate()
            enemyItems.addViewModel(enemyItem)

        model.setEnemies(enemyItems)

    def __setTeamStatsData(self, model):
        allies, enemies = self.__reusable.getBiDirectionTeamsIterator(self.__results['vehicles'])
        items = model.getAllies()
        if items is None:
            return
        else:
            self.__fillTeamStats(items, allies)
            items = model.getEnemies()
            if items is None:
                return
            self.__fillTeamStats(items, enemies)
            return

    def __fillTeamStats(self, items, data):
        items.clear()
        for idx, info in enumerate(data):
            if info.player.dbID == 0:
                continue
            player = PlayerModel()
            player.setIdx(idx)
            player.setDbID(info.player.dbID)
            playerTeam = info.player.team
            player.setTeam(playerTeam)
            player.setSquadIdx(info.player.squadIndex)
            if playerTeam == self.__reusable.getPersonalTeam():
                personalInfo = self.__reusable.getPlayerInfo()
                isPersonal = personalInfo.dbID == info.player.dbID
                player.setIsPersonal(isPersonal)
                player.setIsSameSquad(isOwnSquad(self.__reusable, info.vehicleID) and not isPersonal)
            setBaseUserInfo(player.user, info.vehicleID, self.__reusable)
            player.setVehicleName(info.vehicle.name)
            player.setLocalizedVehicleName(getSimpleShortUserName(info.vehicle))
            player.setVehicleLevel(info.vehicle.level)
            player.setVehicleType(info.vehicle.type)
            player.setVehicleCD(info.vehicle.intCD)
            player.setEarnedXp(info.xp)
            player.setKills(info.kills)
            player.setDamageDealt(info.damageDealt)
            setTeamStatsAchievements(player.details, info)
            self.__fillPlayerDetails(player.details, info)
            items.addViewModel(player)

        items.invalidate()

    def __fillPlayerDetails(self, detailBlock, info):
        detailBlock.setAttackReason(info.deathReason)
        if isPersonalResults(self.__reusable, info.player.dbID):
            detailBlock.setIsLeftBattle(isPlayerLeftBattle(self.__reusable))
        killerVehicleID = info.killerID
        if killerVehicleID:
            setBaseUserInfo(detailBlock.killer, killerVehicleID, self.__reusable)
        self.__fillStatistics(detailBlock, info)

    def __fillStatistics(self, model, info):
        items = Array()
        personalInfo = self.__reusable.getPlayerInfo()
        personalDBID = personalInfo.dbID
        isPersonal = info.player.dbID == personalDBID
        isSPG = info.vehicle.type == VEHICLE_CLASS_NAME.SPG
        isRoleExp = self.__reusable.common.arenaVisitor.bonus.hasRoleExpSystem()
        for field in self.__getter.getTeamStats(isSPG, isPersonal, isRoleExp):
            statsItem = field.model()
            statsItem.setValue(field.getFieldValues(info, self.__results))
            statsItem.setItemType(field.valueType)
            statsItem.setBlockIdx(field.blockIdx)
            statsItem.setId(field.stringID)
            statsItem.setHasTooltip(field.hasTooltip)
            items.addViewModel(statsItem)

        model.setStatistics(items)

    def __getCurrentQuests(self, groupIDs):
        questController = dependency.instance(IQuestsController)

        def filterFunc(quest):
            return quest.isEventBattlesQuest() and quest.getGroupID() in groupIDs and (quest.isCompleted() or quest.accountReqs.isAvailable())

        quests = questController.eventsCache.getAllQuests(filterFunc).items()
        return quests

    def __getQuestsData(self, tooltipData):
        eventsList = []
        isBoss = self.__reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
        if isBoss:
            availableQuests = self.__getQuests(WT_BOSS_GROUP_ID)
        else:
            availableQuests = []
            for chainID in HUNTER_QUEST_CHAINS:
                harrierQuests = self.__getQuests(chainID, reverse=True)
                if not harrierQuests:
                    harrierQuests = self.__getQuests(chainID, reverse=True)
                if not harrierQuests:
                    _logger.error("Can't find quests for group %s", chainID)
                    continue
                availableQuests.append(harrierQuests[0])

        availableQuests = availableQuests[:MAX_VISIBLE_QUESTS]
        for _, quest in availableQuests:
            packer = WTEventBattleQuestUIDataPacker(quest)
            model = WtEventQuestModel()
            eventsList.append(packer.pack(model))
            tooltipData[quest.getID()] = packer.getTooltipData()
            if quest.isCompleted():
                model.setStatus(EventStatus.DONE)
                self.__eventsCache.questsProgress.markQuestProgressAsViewed(quest.getID())
            model.setCompletedMissions(quest.getBonusCount())
            model.setMaxMissions(quest.bonusCond.getBonusLimit())

        return eventsList

    def __getQuests(self, groupID, reverse=False):

        def filterQuests(quest):
            return quest.getGroupID() == groupID and quest.isStarted() and quest.accountReqs.isAvailable()

        quests = self.__eventsCache.getAllQuests(filterQuests).items()
        return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)

    def __setEventsData(self, model, tooltipData):
        dataItems = self.__getQuestsData(tooltipData)
        for data in dataItems:
            model.getEvents().addViewModel(data)

        with model.transaction() as mod:
            isBoss = self.__reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
            currentQuests = self.__getCurrentQuests([WT_BOSS_GROUP_ID]) if isBoss else self.__getCurrentQuests(HUNTER_QUEST_CHAINS)
            progressData = self.__reusable.personal.getQuestsProgress()
            isAllQuestsCompletedBeforeBattle = all((quest.isCompleted() and qID not in progressData for qID, quest in currentQuests))
            model.setHasQuestsToShow(not isAllQuestsCompletedBeforeBattle)
            mod.setQuestsUpdateTimeLeft(EventInfoModel.getDailyProgressResetTimeDelta())
            mod.setIsHunter(self.__reusable.getPersonalTeam() == WT_TEAMS.HUNTERS_TEAM)

    @property
    def __getter(self):
        if self.__fieldsGetter is None:
            self.__fieldsGetter = createFieldsGetter()
        return self.__fieldsGetter

    def __handleBattleResultsPosted(self, reusableInfo, _, __):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID:
            Waiting.hide('stats')
            with self.getViewModel().transaction() as model:
                self.__setDataModel(model)

    def _initialize(self, *args, **kwargs):
        super(WtBattleResultView, self)._initialize(*args, **kwargs)
        self.__addListeners()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__battleResults.onResultPosted -= self.__handleBattleResultsPosted
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.__removeListeners()
        self.__arenaUniqueID = None
        self.__tooltipParametersCreator = None
        self.__tooltipContentCreator = None
        self.__eventPlugin.finalize()
        self.__eventPlugin = None
        if self.__fieldsGetter is not None:
            self.__fieldsGetter.clear()
            self.__fieldsGetter = None
        super(WtBattleResultView, self)._finalize()
        return

    def __addListeners(self):
        viewModel = self.viewModel
        viewModel.onChangeCurrentTab += self.__onChangeCurrentTab
        viewModel.common.rewards.onAppliedPremiumBonus += self.__onAppliedPremiumBonus
        viewModel.details.premiumBonuses.onBuyPremium += self.__onBuyPremiumPlus
        self.__eventPlugin.addListeners()
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
        self.__battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.__eventPlugin.removeListeners()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChange
        self.__gameSession.onPremiumTypeChanged -= self.__onPremiumStateChanged
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onUpdatePremiumBonus)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onChangeCurrentTab(self, args=None):
        tabId = args.get('tabId')
        if tabId is None:
            raise SoftException('Invalid arguments to extract an index of the tab')
        if tabId == PostbattleScreenModel.PERSONAL_TAB:
            with self.getViewModel().transaction() as model:
                model.common.generalInfo.setServerTime(time_utils.getServerUTCTime())
                applyAdditionalXPCount = self.__itemsCache.items.stats.applyAdditionalXPCount
                isActivePremiumPlus = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
                if isActivePremiumPlus and applyAdditionalXPCount == 0:
                    nextBonusTime = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
                    model.common.rewards.expBonus.setNextBonusTime(nextBonusTime)
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

    def __getTooltipParameters(self, event):
        tooltipID = event.getArgument('tooltipId')
        if isWtEventBattleQuest(tooltipID):
            questBnsTooltipData = self.__getQuestBonusTooltipData(tooltipID)
            if questBnsTooltipData is not None:
                return questBnsTooltipData
        parametersCreator = self.__tooltipParametersCreator.get(tooltipID)
        if parametersCreator is None:
            raise SoftException('Invalid arguments to create an old flash tooltip with id {}'.format(tooltipID))
        return parametersCreator(event)

    def __getQuestBonusTooltipData(self, tooltipID):
        ids = tooltipID.rsplit(':', 1)
        if len(ids) != 2:
            _logger.error('TooltipId argument has invalid format.')
            return None
        else:
            questId, tIdx = ids
            questData = self.__questBnsTooltipData.get(questId, {})
            return questData.get(tIdx)

    def __getTooltipContentCreator(self):
        rPostBattle = R.views.white_tiger.lobby.postbattle.tooltips
        creatorMap = {rPostBattle.ProgressiveReward(): self.__getProgressiveRewardTooltipContent,
         rPostBattle.PersonalEfficiency(): self.__getPersonalEfficiencyTooltipContent,
         rPostBattle.ExpBonus(): self.__getPremiumBonusTooltipContent,
         rPostBattle.PremiumPlus(): self.__getPremiumPlusTooltipContent,
         rPostBattle.FinanceDetails(): self.__getFinanceDetailsTooltipContent}
        creatorMap.update(self.__eventPlugin.getContentTooltipCreator())
        return creatorMap

    def __getTooltipParametersCreator(self):
        return {AchievementModel.ACHIEVEMENT_TOOLTIP: self.__getAchievementTooltipParameters,
         DetailedPersonalEfficiencyModel.EFFICIENCY_PARAM_TOOLTIP: self.__getEfficiencyTooltipParameters,
         DetailedPersonalEfficiencyModel.EFFICIENCY_HEADER_PARAM_TOOLTIP: self.__getEfficiencyTooltipParameters,
         DetailedPersonalEfficiencyModel.TOTAL_EFFICIENCY_PARAM_TOOLTIP: self.__getTotalEfficiencyTooltipParameters}

    def __getAchievementTooltipParameters(self, event):
        achievementID = int(event.getArgument('achievementID'))
        achievementName = event.getArgument('achievementName')
        isPersonal = event.getArgument('isPersonal')
        args = getAchievementTooltipData(achievementID, achievementName, isPersonal, self.__reusable, self.__results)
        return createTooltipData(isSpecial=True, specialAlias=getAchievementTooltipType(achievementName), specialArgs=args)

    def __getEfficiencyTooltipParameters(self, event):
        args = self.__battleResults.presenter
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EFFICIENCY_PARAM, specialArgs=args)

    def __getTotalEfficiencyTooltipParameters(self, event):
        args = self.__battleResults.presenter
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TOTAL_EFFICIENCY_PARAM, specialArgs=args)

    def __getPersonalEfficiencyTooltipContent(self, event):
        efficiencyType = event.getArgument('parameter')
        return WtEfficiencyTooltip(self.__arenaUniqueID, efficiencyType)

    def __getProgressiveRewardTooltipContent(self, _=None):
        sourceDataModel = self.viewModel.common.rewards.progressiveReward
        return WtRewardsTooltip(sourceDataModel)

    def __getPremiumBonusTooltipContent(self, _=None):
        sourceDataModel = self.viewModel.common.rewards.expBonus
        return WtExpBonusTooltip(sourceDataModel)

    def __getPremiumPlusTooltipContent(self, _=None):
        return WtPremiumPlusTooltip()

    def __getFinanceDetailsTooltipContent(self, event):
        currencyType = event.getArgument('parameter')
        if currencyType is None:
            raise SoftException('Missing currency type for the tooltip.')
        return WtFinancialTooltip(self.__arenaUniqueID, currencyType)
