# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/battle_royale.py
import logging
from collections import defaultdict
import typing
from constants import ARENA_BONUS_TYPE, DEATH_REASON_ALIVE
from gui.battle_control.battle_constants import WinStatus
from gui.battle_results.components import base
from gui.battle_results.components.personal import PersonalVehiclesBlock
from gui.battle_results.components.progress import isQuestCompleted
from gui.battle_results.reusable import sort_keys
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import IEventsCache
from gui.server_events.battle_royale_formatters import SOLO_ITEMS_ORDER, SQUAD_ITEMS_ORDER, StatsItemType
from gui.server_events.events_helpers import isBattleRoyale
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBattleRoyaleController
from ValueReplay import ValueReplay, ValueReplayConnector
from battle_results import g_config as battleResultsConfig
from gui.battle_results.reusable import records
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.battle_results.reusable import _ReusableInfo
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_THE_BEST_RANK = 1

def _isSquadMode(reusable):
    return reusable.common.arenaBonusType in (ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD)


class BattleRoyaleArenaNameBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        geometryName = replaceHyphenToUnderscore(reusable.common.arenaType.getGeometryName())
        return backport.text(R.strings.arenas.num(geometryName).name())


class ArenaBonusTypeNameBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaBonusType = reusable.common.arenaVisitor.getArenaBonusType()
        return arenaBonusType


class PersonalPlayerNameBlock(base.StatsBlock):
    __slots__ = ('userName', 'clanAbbrev')

    def __init__(self, meta=None, field='', *path):
        super(PersonalPlayerNameBlock, self).__init__(meta, field, *path)
        self.userName = ''
        self.clanAbbrev = ''

    def setRecord(self, result, reusable):
        player = reusable.getPlayerInfo()
        self.userName = player.realName
        self.clanAbbrev = player.clanAbbrev


class BattleRoyalePlayerPlaceBlock(base.StatsItem):
    __slots__ = ()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _convert(self, value, reusable):
        playerRank = reusable.personal.avatar.extensionInfo.get('playerRank', 0)
        if self.__sessionProvider.getCtx().extractLastArenaWinStatus() is not None:
            winStatus = WinStatus.WIN if playerRank == _THE_BEST_RANK else WinStatus.LOSE
            self.__sessionProvider.getCtx().setLastArenaWinStatus(WinStatus(winStatus))
        return playerRank


class BattleRoyaleIsSquadModeBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return _isSquadMode(reusable)


class BattleRoyalePersonalVehicleBlock(base.StatsBlock):
    __slots__ = ('vehicleName', 'vehicleType', 'isObserver')

    def __init__(self, meta=None, field='', *path):
        super(BattleRoyalePersonalVehicleBlock, self).__init__(meta, field, *path)
        self.vehicleName = ''
        self.vehicleType = ''
        self.isObserver = False

    def setVehicle(self, item):
        if item is not None:
            self.vehicleName = item.shortUserName
            self.vehicleType = item.type
            self.isObserver = item.isObserver
        return

    def setRecord(self, result, reusable):
        pass


class BattleRoyaleVehiclesBlock(PersonalVehiclesBlock):
    __slots__ = ()

    def _createComponent(self):
        return BattleRoyalePersonalVehicleBlock()


class BattleRoyaleIsPremiumBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.isPostBattlePremium or reusable.isPostBattlePremiumPlus


class BattleRoyaleVehicleStatusBlock(base.StatsBlock):
    __slots__ = ('killer', 'vehicleState', 'isSelfDestroyer')

    def __init__(self, meta=None, field='', *path):
        super(BattleRoyaleVehicleStatusBlock, self).__init__(meta, field, *path)
        self.killer = None
        self.vehicleState = DEATH_REASON_ALIVE
        self.isSelfDestroyer = False
        return

    def setRecord(self, result, reusable):
        playerInfo = reusable.getPlayerInfo()
        vehicleId = reusable.vehicles.getVehicleID(playerInfo.dbID)
        vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
        self.vehicleState = vehicleInfo.deathReason
        killerVehicleID = result[vehicleInfo.intCD]['killerID']
        if killerVehicleID:
            killerInfo = reusable.getPlayerInfoByVehicleID(killerVehicleID)
            isSelf = playerInfo.realName == killerInfo.realName
            isSquad = playerInfo.squadIndex > 0 and playerInfo.squadIndex == killerInfo.squadIndex or isSelf
            if killerInfo.realName == killerInfo.fakeName or isSquad:
                self.killer = {'userName': killerInfo.realName,
                 'clanAbbrev': killerInfo.clanAbbrev}
            else:
                self.killer = {'userName': killerInfo.fakeName,
                 'clanAbbrev': ''}
            self.isSelfDestroyer = killerInfo.realName == playerInfo.realName


class _BRCoinReplayRecords(records.ReplayRecords):
    __slots__ = ()

    def __init__(self, replay, results):
        super(_BRCoinReplayRecords, self).__init__(replay, 'count')
        self._addRecord(ValueReplay.FACTOR, 'premiumFactor100', results['premiumFactor100'], 0)
        self._addRecord(ValueReplay.FACTOR, 'premiumVipFactor100', results['premiumVipFactor100'], 0)
        self._addRecord(ValueReplay.FACTOR, 'premiumPlusFactor100', results['premiumPlusFactor100'], 0)
        self._addRecord(ValueReplay.FACTOR, 'appliedPremiumFactor100', results['appliedPremiumFactor100'], 0)


class BattleRoyaleFinancialBlock(base.StatsBlock):
    __slots__ = ('credits', 'xp', 'crystal', 'brcoin')

    def __init__(self, meta=None, field='', *path):
        super(BattleRoyaleFinancialBlock, self).__init__(meta, field, *path)
        self.credits = 0
        self.xp = 0
        self.crystal = 0
        self.brcoin = 0

    def setRecord(self, result, reusable):
        avatarInfo = result['personal']['avatar']
        self.credits = avatarInfo['credits']
        self.xp = avatarInfo['xp']
        self.crystal = avatarInfo['crystal']
        self.brcoin = self._getBrCoins(result, isPremium=False)

    def _getBrCoins(self, result, isPremium):
        vehicleCD = [ key for key in result['personal'].keys() if isinstance(key, (int, long, float)) ][0]
        info = result['personal'][vehicleCD]
        for code, data in info['currencies'].iteritems():
            if code == 'brcoin':
                meta = battleResultsConfig['allResults'].meta('currencies').meta('brcoin')
                replayConnector = ValueReplayConnector(data, meta)
                replay = ValueReplay(replayConnector, recordName='count', replay=data['replay'])
                if not isPremium:
                    return _BRCoinReplayRecords(replay, data).getRecord('count')
                if 'appliedPremiumFactor100' in replay:
                    replay['appliedPremiumFactor100'] = data['premiumPlusFactor100']
                return _BRCoinReplayRecords(replay, data).getRecord('count')


class BattleRoyaleFinancialPremBlock(BattleRoyaleFinancialBlock):

    def setRecord(self, result, reusable):
        avatarInfo = result['personal']['avatar']
        for rec in reusable.personal.getMoneyRecords():
            _, premiumCredits = rec[:2]
            names = ('originalCredits', 'appliedPremiumCreditsFactor100', 'boosterCreditsFactor100')
            self.credits = premiumCredits.getRecord(*names)

        for rec in reusable.personal.getCrystalRecords():
            _, premiumCrystal = rec[:2]
            self.crystal = premiumCrystal.getRecord('crystal')

        for rec in reusable.personal.getXPRecords():
            _, premiumXP = rec[:2]
            self.xp = premiumXP.getRecord('xpToShow')

        self.brcoin = self._getBrCoins(result, isPremium=True)
        self.credits += avatarInfo.get('eventCredits', 0)


class BattleRoyaleStatsItemBlock(base.StatsBlock):
    __slots__ = ('type', 'value', 'maxValue', 'wreathImage')
    _ICON_PATH = R.images.gui.maps.icons.battleRoyale.battleResult.stat_list
    _DEFAULT_ICON = _ICON_PATH.wreath_transparent

    def __init__(self, itemType, meta=None, field='', *path):
        super(BattleRoyaleStatsItemBlock, self).__init__(meta, field, *path)
        self.type = itemType
        self.value = 0
        self.maxValue = 0
        self.wreathImage = R.invalid()

    def setRecord(self, result, reusable):
        self.value = self._getValue(result, reusable)
        self.maxValue = self._getMaxValue(result, reusable)
        self.wreathImage = self._getWreathImage(result, reusable)

    def _getValue(self, result, reusable):
        pass

    def _getMaxValue(self, result, reusable):
        pass

    def _getWreathImage(self, result, reusable):
        return self._ICON_PATH.wreath_silver() if self._isTop(result, reusable) else self._DEFAULT_ICON()

    def _isTop(self, result, reusable):
        return False


class SimpleEfficiencyParameter(BattleRoyaleStatsItemBlock):
    __slots__ = ()

    def _getValue(self, result, reusable):
        personalInfo = reusable.getPersonalVehiclesInfo(result['personal'])
        return getattr(personalInfo, self.type)

    def _isTop(self, result, reusable):
        if self.value == 0:
            return False
        for player in reusable.getAllPlayersIterator(result['vehicles']):
            playerValue = getattr(player, self.type)
            if playerValue > 0 and playerValue > self.value:
                return False

        return True


class PlaceParameter(BattleRoyaleStatsItemBlock):
    __slots__ = ()

    def _getValue(self, result, reusable):
        personalInfo = reusable.getPersonalVehiclesInfo(result['personal'])
        avatar = personalInfo.avatar
        return avatar.extensionInfo.get('playerRank', 0)

    def _getMaxValue(self, result, reusable):

        def observerFilter(player):
            return not player.vehicle.isObserver

        allPlayers = filter(observerFilter, list(reusable.getAllPlayersIterator(result['vehicles'])))
        return len(set((item.player.team for item in allPlayers))) if _isSquadMode(reusable) else len(allPlayers)

    def _getWreathImage(self, result, reusable):
        return self._ICON_PATH.wreath_gold() if self.value == _THE_BEST_RANK else self._DEFAULT_ICON()


class KilledBySquadParameter(BattleRoyaleStatsItemBlock):
    __slots__ = ()

    def _getValue(self, result, reusable):
        allPlayers = reusable.getAllPlayersIterator(result['vehicles'])
        team = reusable.getPlayerInfo().team
        return sum(list((item.kills for item in allPlayers if team != 0 and team == item.player.team)))

    def _isTop(self, result, reusable):
        if self.value == 0:
            return False
        killesBySquads = defaultdict(int)
        for item in reusable.getAllPlayersIterator(result['vehicles']):
            killesBySquads[item.player.team] += item.kills
            if killesBySquads[item.player.team] > self.value:
                return False

        return True


class BattleRoyaleStatsBlock(base.StatsBlock):
    __slots__ = ()
    _itemsFactory = {StatsItemType.PLACE: PlaceParameter,
     StatsItemType.KILLS_SOLO: SimpleEfficiencyParameter,
     StatsItemType.KILLS_SQUAD: KilledBySquadParameter,
     StatsItemType.DAMAGE_DEAL: SimpleEfficiencyParameter,
     StatsItemType.DAMAGE_BLOCK: SimpleEfficiencyParameter}

    def setRecord(self, result, reusable):
        items = SQUAD_ITEMS_ORDER if _isSquadMode(reusable) else SOLO_ITEMS_ORDER
        for itemType in items:
            classType = self._itemsFactory.get(itemType)
            if classType is None:
                _logger.error('Incorrect parameter of personal efficiency')
            component = classType(itemType)
            component.setRecord(result, reusable)
            self.addComponent(self.getNextComponentIndex(), component)

        return


class BattleRoyaleRewardsBlock(base.StatsBlock):
    __slots__ = ('achievements', 'bonuses', 'completedQuestsCount', 'completedQuests')
    __eventsCache = dependency.descriptor(IEventsCache)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __QUESTS_WITH_MEDALS = frozenset(['br_battle_result_solo_1', 'br_battle_result_squad_1'])

    def __init__(self, meta=None, field='', *path):
        super(BattleRoyaleRewardsBlock, self).__init__(meta, field, *path)
        self.achievements = []
        self.bonuses = []
        self.completedQuestsCount = 0
        self.completedQuests = {}

    def setRecord(self, result, reusable):
        questProgress = reusable.personal.getQuestsProgress()
        allQuests = self.__eventsCache.getAllQuests()
        self.achievements = self.__getAchievements(questProgress, allQuests)
        self.completedQuests = self.__getCompletedQuests(questProgress, self.__getDailyQuestsCondition, allQuests)
        self.completedQuestsCount = len(self.completedQuests)
        self.bonuses = self.__getBonuses(allQuests, self.completedQuests)

    def __getAchievements(self, questProgress, allQuests):
        completedQuestsWithMedals = self.__getCompletedQuests(questProgress, self.__getAchievementQuestsCondition, allQuests)
        if completedQuestsWithMedals:
            allBonuses = self.__getBonuses(allQuests, completedQuestsWithMedals)
            allAchievements = [ bonus.getAchievements() for bonuses in allBonuses for bonus in bonuses if bonus.getName() == 'dossier' ]
            return [ achievement.getName() for achievementList in allAchievements for achievement in achievementList ]
        return []

    def __getAchievementQuestsCondition(self, qID, _):
        return qID in self.__QUESTS_WITH_MEDALS

    def __getDailyQuestsCondition(self, qID, allQuests):
        return isBattleRoyale(allQuests.get(qID).getGroupID())

    @staticmethod
    def __getCompletedQuests(questProgress, condition, allQuests):
        return {qID:qProgress for qID, qProgress in questProgress.iteritems() if condition(qID, allQuests) and isQuestCompleted(*qProgress)}

    @staticmethod
    def __getBonuses(allQuests, completedQuests):
        return [ allQuests.get(qID).getBonuses() for qID in completedQuests ]


class BattlePassBlock(base.StatsBlock):
    __slots__ = ('currentLevel', 'maxPoints', 'earnedPoints', 'currentLevelPoints', 'isDone', 'hasBattlePass', 'battlePassComplete', 'chapterID', 'pointsTotal', 'basePointsDiff')

    def __init__(self, meta=None, field='', *path):
        super(BattlePassBlock, self).__init__(meta, field, *path)
        self.currentLevel = 0
        self.maxPoints = 0
        self.earnedPoints = 0
        self.currentLevelPoints = 0
        self.isDone = False
        self.hasBattlePass = False
        self.battlePassComplete = False
        self.chapterID = 0
        self.pointsTotal = 0
        self.basePointsDiff = 0

    def setRecord(self, result, reusable):
        hasProgress = reusable.battlePassProgress.hasProgress
        showIfEmpty = reusable.common.arenaBonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE
        if hasProgress or showIfEmpty:
            self.currentLevel = reusable.battlePassProgress.currentLevel
            self.maxPoints = reusable.battlePassProgress.pointsMax
            self.earnedPoints = reusable.battlePassProgress.pointsAdd
            self.currentLevelPoints = reusable.battlePassProgress.pointsNew
            self.isDone = reusable.battlePassProgress.isDone
            self.hasBattlePass = reusable.battlePassProgress.hasBattlePass
            self.battlePassComplete = reusable.battlePassProgress.battlePassComplete
            self.chapterID = reusable.battlePassProgress.chapterID
            self.pointsTotal = reusable.battlePassProgress.pointsTotal
            self.basePointsDiff = reusable.battlePassProgress.basePointsDiff


class BattleRoyalePlayerBlock(base.StatsBlock):
    __slots__ = ('isPersonal', 'userName', 'clanAbbrev', 'place', 'isPersonalSquad', 'squadIdx', 'hiddenName', 'achievedLevel', 'kills', 'damage', 'vehicleName', 'vehicleType', 'databaseID')

    def __init__(self, meta=None, field='', *path):
        super(BattleRoyalePlayerBlock, self).__init__(meta, field, *path)
        self.isPersonal = False
        self.userName = ''
        self.hiddenName = ''
        self.clanAbbrev = ''
        self.place = 0
        self.squadIdx = 0
        self.isPersonalSquad = False
        self.achievedLevel = 0
        self.kills = 0
        self.damage = 0
        self.vehicleName = ''
        self.vehicleType = ''
        self.databaseID = 0

    def setRecord(self, vehicleSummarizeInfo, reusable):
        player = vehicleSummarizeInfo.player
        dbID = player.dbID
        if player.realName == player.fakeName:
            self.userName = player.realName
            self.clanAbbrev = player.clanAbbrev
        elif self.isPersonal or self.isPersonalSquad:
            self.userName = player.realName
            self.clanAbbrev = player.clanAbbrev
            self.hiddenName = player.fakeName
        else:
            self.userName = player.fakeName
            self.hiddenName = player.realName
            self.clanAbbrev = ''
        avatarInfo = reusable.avatars.getAvatarInfo(dbID)
        if avatarInfo is not None and avatarInfo.extensionInfo is not None:
            self.place = avatarInfo.extensionInfo.get('playerRank', 0)
        return


class BattleRoyaleTeamStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        allPlayers = reusable.getAllPlayersIterator(result, sortKey=sort_keys.placeSortKey)
        personalInfo = reusable.getPlayerInfo()
        personalDBID = personalInfo.dbID
        team = personalInfo.team if personalInfo.squadIndex else 0
        for item in allPlayers:
            if item.vehicle is not None and item.vehicle.isObserver:
                continue
            block = BattleRoyalePlayerBlock()
            player = item.player
            block.isPersonal = player.dbID == personalDBID
            block.squadIdx = player.team
            block.isPersonalSquad = team != 0 and team == player.team
            block.achievedLevel = item.vehicles[0].achievedLevel
            block.damage = item.damageDealt
            block.kills = item.kills
            block.vehicleName = item.vehicle.shortUserName
            block.vehicleType = item.vehicle.type
            block.databaseID = item.player.dbID
            block.setRecord(item, reusable)
            self.addComponent(self.getNextComponentIndex(), block)

        return
