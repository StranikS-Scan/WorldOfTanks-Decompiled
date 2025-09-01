# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/battle_result_view.py
import WWISE
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, TokensBonus
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.money import Currency
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from last_stand.gui.game_control.ls_difficulty_missions_controller import getFormattedMissionsList
from last_stand.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType
from last_stand.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import LSBonusesAwardsComposer, getLSBattleResultAwardFormatter, getImgName
from last_stand.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from last_stand.gui.impl.lobby.tooltips.difficulty_tooltip import DifficultyTooltipView
from last_stand.gui.impl.lobby.widgets.battle_result_stats import BattleResultStats
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import PBS_ENTER, PBS_EXIT, LastStandVO, DifficultyState
from last_stand.gui.shared.event_dispatcher import showLootBoxMainViewInQueue
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
from last_stand_common.last_stand_constants import ArtefactsSettings, ARENA_BONUS_TYPE_TO_LEVEL, LS_VEHILCE_DAILY_QUEST
from ids_generators import SequenceIDGenerator
from skeletons.gui.battle_results import IBattleResultsService
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from last_stand.gui.impl.lobby.base_view import BaseView
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_R_KEY_TOOLTIP = R.views.last_stand.mono.lobby.tooltips.key_tooltip()

class BattleResultView(BaseView):
    __slots__ = ('__arenaUniqueID', '__bonusCache', '__idGen', '__tooltipCtx')
    battleResults = dependency.descriptor(IBattleResultsService)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventBattlesController = dependency.descriptor(IEventBattlesController)
    settingsCore = dependency.descriptor(ISettingsCore)
    lsCtrl = dependency.descriptor(ILSController)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lsDifficultyMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)
    _MAX_BONUSES_IN_VIEW = 7
    __sound_env__ = BattleResultsEnv

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID or R.views.last_stand.mono.lobby.battle_result_view())
        settings.flags = ViewFlags.VIEW
        settings.model = BattleResultViewModel()
        super(BattleResultView, self).__init__(settings)
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self.__tooltipCtx = {}
        self.__arenaUniqueID = ctx['arenaUniqueID']

    @property
    def viewModel(self):
        return super(BattleResultView, self).getViewModel()

    def createContextMenu(self, event):
        statsView = self.getChildView(R.aliases.last_stand.shared.TeamStats())
        return statsView.createContextMenu(event)

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(BattleResultView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.difficulty_tooltip():
            totalVO = self.battleResults.getResultsVO(self.__arenaUniqueID)
            return DifficultyTooltipView(isHangar=False, difficulty=ARENA_BONUS_TYPE_TO_LEVEL[totalVO['common']['bonusType']], completedMissions=totalVO['completedDifficultyMissions'])
        if contentID == _R_KEY_TOOLTIP:
            return KeyTooltipView(isPostBattle=True, ctx=self.__tooltipCtx.get(contentID, {}))
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(BattleResultView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__fillViewModel()
        self.setChildView(resourceID=R.aliases.last_stand.shared.TeamStats(), view=BattleResultStats(arenaUniqueID=self.__arenaUniqueID))

    def _initialize(self, *args, **kwargs):
        super(BattleResultView, self)._initialize()
        playSound(PBS_ENTER)

    def _finalize(self):
        playSound(PBS_EXIT)
        super(BattleResultView, self)._finalize()

    def _subscribe(self):
        super(BattleResultView, self)._subscribe()
        self.viewModel.onClose += self._onClose

    def _unsubscribe(self):
        self.viewModel.onClose -= self._onClose
        super(BattleResultView, self)._unsubscribe()

    def __fillViewModel(self):
        totalVO = self.battleResults.getResultsVO(self.__arenaUniqueID)
        with self.viewModel.transaction() as model:
            self.__fillCommonInfo(model, totalVO)
            self.__fillPlayerInfo(model.playerInfo, totalVO)
            self.__fillRewardsInfo(model.getRewards(), totalVO)
            self.__playVoiceover(totalVO)

    def __fillCommonInfo(self, model, totalVO):
        commonVO = totalVO['common']
        isWin = commonVO['resultShortStr'] == PLAYER_TEAM_RESULT.WIN
        model.setIsWin(isWin)
        model.battleInfo.setStartDate(commonVO['arenaCreateTimeStr'])
        model.battleInfo.setDuration(commonVO['duration'])
        difficulty = ARENA_BONUS_TYPE_TO_LEVEL[commonVO['bonusType']]
        model.setDifficultyLevel(difficulty)
        model.setCurrentPhase(totalVO['phase'])
        model.setPhasesCount(totalVO['phasesCount'])
        personalVO = self.__getPersonalVO(totalVO)
        if personalVO['hasPenalties']:
            completedPhaseCnt = totalVO['phase'] - 1 * (not isWin)
            isNewRecord = completedPhaseCnt > totalVO['prevBestMissionsCount']
            model.setNewRecord(isNewRecord)
            if isNewRecord:
                model.setCompletedMissions('|'.join((str(idx) for idx in xrange(0, completedPhaseCnt))))
        else:
            model.setCompletedMissions(getFormattedMissionsList(totalVO['completedDifficultyMissions']))
            model.setNewRecord(len(totalVO['completedDifficultyMissions']) > totalVO['prevBestMissionsCount'])
        model.setTime(totalVO['time'])

    def __fillPlayerInfo(self, playerInfo, totalVO):
        personalVO = self.__getPersonalVO(totalVO)
        playerInfo.user.setUserName(personalVO['playerName'])
        playerInfo.user.setClanAbbrev(personalVO['clanAbbrev'])
        playerInfo.vehicle.setVehicleName(personalVO['vehicleName'])
        playerInfo.vehicle.setVehicleShortName(personalVO['vehicleShortName'])
        if personalVO.get('vehicleIsIGR', False):
            playerInfo.vehicle.setTags(VEHICLE_TAGS.PREMIUM_IGR)
        playerInfo.vehicle.setVehicleType(personalVO['vehicleType'])
        vehicleItem = self.itemsCache.items.getItemByCD(personalVO['vehicleCD'])
        playerInfo.vehicle.setVehicleIconName(vehicleItem.name.replace(':', '_'))
        playerInfo.setRespCount(personalVO['respawnsCount'])
        banType = TeamMemberBanType.NOTBANNED if not personalVO['hasPenalties'] else TeamMemberBanType.BANNED
        playerInfo.setBanType(banType)

    def __fillRewardsInfo(self, model, totalVO):
        rewardsVO = totalVO['rewards']
        effectivenessKeys = rewardsVO['effectivenessKeys']
        keysBonus = self.__getKeysBonus(effectivenessKeys)
        vehicleDailyQuestBonuses, otherDailyQuestBonuses = self.__getQuestBonuses(totalVO['quests'])
        creditsBonus = self.__getCreditsBonus(rewardsVO['credits'])
        totalBonuses = creditsBonus + keysBonus + vehicleDailyQuestBonuses + otherDailyQuestBonuses
        self.__checkLootBox(totalBonuses)
        self.__tooltipCtx[_R_KEY_TOOLTIP] = {'effective': effectivenessKeys,
         'vehicleDaily': self.__getDailyKeys(vehicleDailyQuestBonuses),
         'missionDaily': self.__getDailyKeys(otherDailyQuestBonuses)}
        model.clear()
        sortedBonuses = sorted(mergeBonuses(totalBonuses), cmp=compareBonusesByPriority)
        formatter = LSBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getLSBattleResultAwardFormatter())
        bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
        for bonus in bonusRewards:
            rewardItem = BonusItemViewModel()
            tooltipId = '{}'.format(self.__idGen.next())
            self.__bonusCache[tooltipId] = bonus
            rewardItem.setName(bonus.bonusName)
            rewardItem.setValue(str(bonus.label))
            rewardItem.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
            rewardItem.setTooltipId(tooltipId)
            if isinstance(bonus.tooltip, int):
                rewardItem.setTooltipContentId(str(bonus.tooltip))
            model.addViewModel(rewardItem)

        model.invalidate()

    def __playVoiceover(self, totalVO):
        commonVO = totalVO['common']
        WWISE.WW_setState(DifficultyState.GROUP, DifficultyState.VALUE(commonVO['bonusType']))
        if commonVO['resultShortStr'] == PLAYER_TEAM_RESULT.WIN:
            playSound(LastStandVO.WIN)
        else:
            playSound(LastStandVO.LOSE)

    def __getLeaderboardPosition(self, players, personal, field):
        leaderboard = sorted(players, key=lambda block: block[field], reverse=True)
        return leaderboard.index(personal) + 1

    def __getCreditsBonus(self, credits):
        return getNonQuestBonuses(Currency.CREDITS, credits) if credits > 0 else []

    def __getKeysBonus(self, keys):
        return getNonQuestBonuses(TokensBonus.TOKENS, {ArtefactsSettings.KEY_TOKEN: {'count': keys}}) if keys > 0 else []

    def __getQuestBonuses(self, quests):
        vehicleDailyQuestBonuses = []
        otherDailyQuestBonuses = []
        for questProgress in quests:
            questID = questProgress['questInfo']['questID']
            quest = self.eventsCache.getAllQuests().get(questID)
            if not quest or not questProgress['awards']:
                continue
            bonuses = quest.getBonuses()
            if questID == LS_VEHILCE_DAILY_QUEST:
                vehicleDailyQuestBonuses.extend(self.__filterBonuses(bonuses, exclude=['credits']))
            otherDailyQuestBonuses.extend(self.__filterBonuses(bonuses, exclude=['credits']))

        return (vehicleDailyQuestBonuses, otherDailyQuestBonuses)

    def __checkLootBox(self, bonuses):
        if any((bonus.getName() == 'lootBox' for bonus in bonuses)) and not self.lsDifficultyMissionsCtrl.isArenaIDInCache(self.__arenaUniqueID):
            self.lsDifficultyMissionsCtrl.addArenaIDToCache(self.__arenaUniqueID)
            showLootBoxMainViewInQueue(self.lsCtrl.lootBoxesEvent)

    def __getKeyCountFromTokens(self, tokens):
        artefactKeyToken = tokens.get(ArtefactsSettings.KEY_TOKEN)
        return artefactKeyToken.count if artefactKeyToken else 0

    def __getDailyKeys(self, bonuses):
        return sum((self.__getKeyCountFromTokens(bonus.getTokens()) for bonus in bonuses if bonus.getName() == 'battleToken'))

    def __getPersonalVO(self, totalVO):
        return next((player for player in totalVO['players'] if player['isPlayer']), None)

    def __filterBonuses(self, bonuses, exclude=None):
        if not exclude:
            return bonuses
        result = []
        for bonus in bonuses:
            if bonus.getName() in exclude:
                continue
            result.append(bonus)

        return result
