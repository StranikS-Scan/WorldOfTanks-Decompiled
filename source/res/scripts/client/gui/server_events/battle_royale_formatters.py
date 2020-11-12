# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/battle_royale_formatters.py
import logging
from collections import defaultdict, namedtuple
import battle_royale_common
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import BattleRoyaleKeys
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE, VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.leaderboard_constants import LeaderboardConstants
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_StatsItemValues = namedtuple('_StatsItemValues', ('value', 'maxValue'))
_NO_MAX_VALUE = -1

class _BattleRewardConstants(object):
    XP = 'xp'
    CREDITS = 'credits'
    PROGRESSION = 'progression'


class StatsItemType(object):
    PLACE = 'place'
    KILLS_SOLO = 'kills'
    KILLS_SQUAD = 'squadKills'
    DAMAGE_DEAL = 'damageDealt'
    DAMAGE_BLOCK = 'damageBlockedByArmor'


SOLO_ITEMS_ORDER = [StatsItemType.PLACE,
 StatsItemType.KILLS_SOLO,
 StatsItemType.DAMAGE_DEAL,
 StatsItemType.DAMAGE_BLOCK]
SQUAD_ITEMS_ORDER = [StatsItemType.PLACE,
 StatsItemType.KILLS_SOLO,
 StatsItemType.KILLS_SQUAD,
 StatsItemType.DAMAGE_DEAL,
 StatsItemType.DAMAGE_BLOCK]

class BRSections(object):
    FINISH_REASON = 'finishReason'
    COMMON = 'common'
    PERSONAL = 'personal'
    STATS = 'stats'
    PROGRESS = 'eventProgression'
    LEADERBOARD = 'leaderboard'
    IN_BATTLE = 'inBattle'
    FINANCE = 'financialBalance'
    REWARDS = 'rewards'
    ACHIEVEMENTS = 'achievements'
    BONUSES = 'bonuses'


def createEmptyPlayerInfo(place=0, clan='', isInSquad=False):
    return {'userName': '',
     'clanAbbrev': clan,
     'place': place,
     'type': LeaderboardConstants.ROW_TYPE_BR_ENEMY,
     'isPersonal': False,
     'isPersonalSquad': isInSquad}


class IngameBattleRoyaleResultsViewDataFormatter(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, sessionProvider, bonusQuestById):
        self.__arenaDP = sessionProvider.getArenaDP()
        self.__ctx = sessionProvider.getCtx()
        self.__playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        self.__killerId, self.__killReason = self.__getKillInfo(sessionProvider)
        self.__efficiencyCtrl = sessionProvider.shared.personalEfficiencyCtrl
        self.__bonusByQuestId = bonusQuestById or {}
        self.__playerPlace = self.__getPlayerPlace(self.__playerVehicleID)
        self.__statsGetters = {StatsItemType.PLACE: self.__getPlace,
         StatsItemType.KILLS_SOLO: self.__getKilled,
         StatsItemType.KILLS_SQUAD: self.__getSquadKills,
         StatsItemType.DAMAGE_DEAL: self.__getDamageDealt,
         StatsItemType.DAMAGE_BLOCK: self.__getBlockedDamage}

    @property
    def isInSquad(self):
        vInfoVO = self.__arenaDP.getVehicleInfo()
        return vInfoVO.isSquadMan()

    @property
    def isWinner(self):
        return self.__playerPlace <= 1

    @property
    def playersCount(self):
        return vos_collections.ActiveVehiclesItemsCollection().count(self.__arenaDP)

    def getInfo(self):
        info = {BRSections.FINISH_REASON: self.getResultsTitle(),
         BRSections.COMMON: self.getVehicleStatus(),
         BRSections.FINANCE: self.getBattleReward(),
         BRSections.STATS: self.getSummaryStats(),
         BRSections.LEADERBOARD: self.getLeaderboard(),
         BRSections.IN_BATTLE: self.getIsInBattle()}
        return info

    def getVehicleStatus(self):
        if self.__killerId is None and self.__killReason is None:
            return {}
        else:
            player = self.__ctx.getPlayerFullNameParts(self.__playerVehicleID)
            isSelfDestroyer = False
            if player.playerFakeName and player.playerFakeName != player.playerName:
                hiddenName = player.playerFakeName
            else:
                hiddenName = ''
            if self.__killerId is not None and self.__killerId != 0:
                killer = self.__ctx.getPlayerFullNameParts(self.__killerId)
                isSelfDestroyer = killer.playerName == player.playerName
                isSquad = isSelfDestroyer or self.__arenaDP.isAlly(self.__killerId)
                if isSquad or killer.playerName == killer.playerFakeName:
                    killerName = killer.playerName
                    killerClan = killer.clanAbbrev
                else:
                    killerName = killer.playerFakeName
                    killerClan = ''
            else:
                killerName, killerClan = ('', '')
            return {'isSquadMode': self.isInSquad,
             'userName': player.playerName,
             'hiddenName': hiddenName,
             'userClanAbbrev': player.clanAbbrev,
             'vehicleStatus': {'vehicleState': self.__killReason,
                               'killer': {'userName': killerName,
                                          'clanAbbrev': killerClan},
                               'isSelfDestroyer': isSelfDestroyer}}

    def getLeaderboard(self):
        leaderboard = {'group_list': self.__getGroupLists()}
        return leaderboard

    def getResultsTitle(self):
        if self.isWinner:
            return R.strings.battle_royale.battleResult.title.victory()
        return R.strings.battle_royale.battleResult.title.squadDestroyed() if self.isInSquad else R.strings.battle_royale.battleResult.title.vehicleDestroyed()

    def getBattleReward(self):
        if self.isInSquad:
            template = battle_royale_common.BR_SQUAD_QUEST_FOR_POSITION_TEMPLATE
        else:
            template = battle_royale_common.BR_SOLO_QUEST_FOR_POSITION_TEMPLATE
        rewards = self.__bonusByQuestId.get(template.format(position=self.__playerPlace), {})
        result = {_BattleRewardConstants.XP: rewards.get(_BattleRewardConstants.XP, 0),
         _BattleRewardConstants.CREDITS: rewards.get(_BattleRewardConstants.CREDITS, 0)}
        result.update(self.__calculateProgression())
        return result

    def getSummaryStats(self):
        items = SQUAD_ITEMS_ORDER if self.isInSquad else SOLO_ITEMS_ORDER
        return [ self.__createStatItem(itemType, self.__statsGetters[itemType]()) for itemType in items ]

    def getIsInBattle(self):
        return True

    def __getPlace(self):
        maxValue = self.__arenaDP.getNumberOfSquads() if self.isInSquad else self.playersCount
        return _StatsItemValues(value=self.__playerPlace, maxValue=maxValue)

    def __getKilled(self):
        return _StatsItemValues(self.__arenaDP.getVehicleStats().frags, _NO_MAX_VALUE)

    def __getBlockedDamage(self):
        return _StatsItemValues(self.__efficiencyCtrl.getTotalEfficiency(_ETYPE.BLOCKED_DAMAGE), _NO_MAX_VALUE)

    def __getDamageDealt(self):
        return _StatsItemValues(self.__efficiencyCtrl.getTotalEfficiency(_ETYPE.DAMAGE), _NO_MAX_VALUE)

    def __getSquadKills(self):
        allies = vos_collections.AllyItemsCollection()
        frags = sum([ vStatsVO.frags for vInfoVO, vStatsVO in allies.iterator(self.__arenaDP) if not vInfoVO.isObserver() and vInfoVO.isSquadMan() ])
        return _StatsItemValues(frags, _NO_MAX_VALUE)

    def __getGroupLists(self):
        return self.__getSquadGroupLists() if self.isInSquad else self.__getSoloGroupLists()

    def __getSoloGroupLists(self):
        settings = self.__lobbyContext.getServerSettings().battleRoyale
        brPointsByPlace = settings.eventProgression.get('brPointsChangesByPlace', ())
        groups = []
        deadVehicles = self.__getDeadPlayersVehicles()
        groupParams = defaultdict(int)
        for points in brPointsByPlace:
            groupParams[points] += 1

        lowestPlace = brPointsByPlace.__len__()
        playersCount = self.playersCount
        if playersCount > lowestPlace:
            groupParams[brPointsByPlace[-1]] += playersCount - lowestPlace
            lowestPlace = playersCount
        deadVehicleIndex = 0
        currentPlace = lowestPlace
        for reward in sorted(groupParams.keys()):
            groupSize = groupParams[reward]
            if currentPlace - groupSize >= playersCount:
                reward = 0
            group = self.__createGroupInfo(reward)
            players = []
            for _ in range(0, groupSize):
                place = currentPlace if currentPlace > 1 else 0
                playerInfo = createEmptyPlayerInfo(place)
                if currentPlace <= playersCount and deadVehicleIndex < deadVehicles.__len__():
                    playerInfo = self.__getPlayerInfo(deadVehicles[deadVehicleIndex])
                    deadVehicleIndex += 1
                players.insert(0, playerInfo)
                currentPlace -= 1

            group['players_list'] = [] if currentPlace == 0 and players[0]['userName'] == '' else players
            groups.insert(0, group)

        return groups

    def __getSquadGroupLists(self):
        settings = self.__lobbyContext.getServerSettings().battleRoyale
        brPointsByPlace = settings.eventProgression.get('brPointsChangesBySquadPlace', ())
        groups = []
        deadSquads = self.__getDeadVehiclesSquads()
        for place, points in enumerate(brPointsByPlace, start=1):
            playerInfo, hasPlayer = self.__getSquadPlayerList(place, deadSquads)
            group = self.__createGroupInfo(points, place, hasPlayer)
            group['players_list'] = [] if place == 1 and playerInfo.__len__() == 0 else playerInfo
            groups.append(group)

        return groups

    def __getDeadVehiclesSquads(self):
        squads = defaultdict(list)
        for infoVO, _ in self.__arenaDP.getActiveVehiclesGenerator():
            squads[infoVO.team].append(infoVO)

        result = {}
        for _, members in squads.iteritems():
            ranks = [ self.__getPlayerPlace(m.vehicleID) for m in members ]
            if min(ranks) == 0:
                continue
            result[min(ranks)] = sorted(members, key=lambda member: self.__getPlayerPlace(member.vehicleID))

        return result

    def __getDeadPlayersVehicles(self):
        return sorted([ infoVO for infoVO, _ in self.__arenaDP.getActiveVehiclesGenerator() if self.__getPlayerPlace(infoVO.vehicleID) != 0 ], key=lambda infoVO: self.__getPlayerPlace(infoVO.vehicleID), reverse=True)

    def __getSquadPlayerList(self, place, deadSquads):
        lastPlace = self.__arenaDP.getNumberOfSquads()
        if place > lastPlace:
            return ([], False)
        sortedPlaces = sorted(deadSquads.keys())
        desiredIndex = lastPlace - place - len(sortedPlaces) + 1
        if place < lastPlace - len(sortedPlaces) + 1:
            return ([], False)
        players = []
        hasPlayer = False
        squadPlace = sortedPlaces[desiredIndex]
        for vInfo in deadSquads[squadPlace]:
            playerInfo = self.__getPlayerInfo(vInfo)
            players.append(playerInfo)
            hasPlayer |= vInfo.vehicleID == self.__playerVehicleID

        return (players, hasPlayer)

    def __getPlayerInfo(self, vInfo):
        userPlace = self.__getPlayerPlace(vInfo.vehicleID)
        fullName = self.__ctx.getPlayerFullNameParts(vInfo.vehicleID)
        info = createEmptyPlayerInfo(userPlace)
        if vInfo.vehicleID == self.__playerVehicleID:
            info['isPersonal'] = True
        elif self.__arenaDP.isAlly(vInfo.vehicleID):
            info['isPersonalSquad'] = True
        if fullName.playerName == fullName.playerFakeName:
            info['userName'] = fullName.playerName
            info['clanAbbrev'] = fullName.clanAbbrev
        elif info['isPersonal'] or info['isPersonalSquad']:
            info['userName'] = fullName.playerName
            info['clanAbbrev'] = fullName.clanAbbrev
            info['hiddenName'] = fullName.playerFakeName
        else:
            info['userName'] = fullName.playerFakeName
        return info

    def __calculateProgression(self):
        settings = self.__lobbyContext.getServerSettings().battleRoyale
        if self.isInSquad:
            brPointsByPlace = settings.eventProgression.get('brPointsChangesBySquadPlace', ())
        else:
            brPointsByPlace = settings.eventProgression.get('brPointsChangesByPlace', ())
        value = 0
        if self.__playerPlace <= brPointsByPlace.__len__():
            value = brPointsByPlace[self.__playerPlace - 1]
        return {_BattleRewardConstants.PROGRESSION: value}

    def __getPlayerPlace(self, vehID):
        return self.__arenaDP.getVehicleStats(vehID).gameModeSpecific.getValue(BattleRoyaleKeys.RANK.value)

    @staticmethod
    def __getKillInfo(sessionProvider):
        ctrl = sessionProvider.shared.vehicleState
        if ctrl is not None:
            deathInfo = ctrl.getStateValue(VEHICLE_VIEW_STATE.DEATH_INFO)
            if deathInfo:
                return (deathInfo['killerID'], deathInfo['reason'])
        ctrl = sessionProvider.shared.feedback
        if ctrl is not None:
            missedEvent = ctrl.getCachedEvent(FEEDBACK_EVENT_ID.POSTMORTEM_SUMMARY)
            if missedEvent:
                return (missedEvent.getKillerID(), missedEvent.getDeathReasonID())
        _logger.error('Cannot obtain kill information not from vehicle state neither from events cache')
        return (None, None)

    @staticmethod
    def __createGroupInfo(reward, place=0, hasPlayer=False):
        return {'place': place,
         'rewardCount': reward,
         'isPersonalSquad': hasPlayer,
         'players_list': []}

    @staticmethod
    def __createStatItem(itemType, values):
        return {'type': itemType,
         'value': values.value,
         'maxValue': values.maxValue,
         'wreathImage': R.images.gui.maps.icons.battleRoyale.battleResult.stat_list.wreath_transparent()}
