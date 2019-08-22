# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/battle_royale_formatters.py
import logging
import battle_royale_common
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.battle_royale.royale_models import TitleData
from gui.impl.auxiliary.rewards_helper import getRoyaleBonuses, getRoyaleBonusesFromDict
from gui.impl.gen import R
from gui.server_events.bonuses import mergeBonuses
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class IPlaceFinder(object):

    @classmethod
    def getPlace(cls, vInfoVO, arenaDP):
        pass

    @classmethod
    def getTotalCount(cls, arenaDP):
        pass


class SquadPlaceFinder(IPlaceFinder):

    @classmethod
    def getPlace(cls, vInfoVO, arenaDP):

        def getBestTeamDO(teamDO):
            return 0 if 0 in teamDO else max(teamDO)

        squadCount = cls._getSquadCount(arenaDP)
        if squadCount == 0:
            return 0
        teamDOByTeamID = {}
        for infoVO, _ in arenaDP.getVehiclesItemsGenerator():
            teamDO = teamDOByTeamID.setdefault(infoVO.team, [])
            teamDO.append(infoVO.events.get('deathOrder', 0))

        if getBestTeamDO(teamDOByTeamID.get(vInfoVO.team, [])) == 0:
            return 0
        deadTeamsBestDO = [ (teamID, getBestTeamDO(teamDO)) for teamID, teamDO in teamDOByTeamID.iteritems() if getBestTeamDO(teamDO) != 0 ]
        sortedBestDO = sorted(deadTeamsBestDO, key=lambda i: i[1])
        playersTeamIndex = [ teamID for teamID, _ in sortedBestDO ].index(vInfoVO.team)
        return squadCount - playersTeamIndex

    @classmethod
    def getTotalCount(cls, arenaDP):
        return cls._getSquadCount(arenaDP)

    @staticmethod
    def _getSquadCount(arenaDP):
        return arenaDP.getNumberOfSquads()


class SoloPlaceFinder(IPlaceFinder):

    @classmethod
    def getPlace(cls, vInfoVO, arenaDP):
        deathOrder = vInfoVO.events.get('deathOrder', 0)
        usersCount = cls._getUsersCount(arenaDP)
        return 0 if usersCount == 0 or deathOrder == 0 else usersCount - (deathOrder - 1)

    @classmethod
    def getTotalCount(cls, arenaDP):
        return cls._getUsersCount(arenaDP)

    @staticmethod
    def _getUsersCount(arenaDP):
        colection = vos_collections.VehiclesItemsCollection()
        return colection.count(arenaDP)


def createPlaceFinder(arenaDP):
    vInfoVO = arenaDP.getVehicleInfo()
    return SquadPlaceFinder if vInfoVO.isSquadMan() else SoloPlaceFinder


class BattleRoyaleScoreFormatter(object):

    def getInfo(self):
        info = {'inBattle': self.getInBattle(),
         'isInSquad': self.getIsInSquad(),
         'isWinner': self.getIsWinner(),
         'dataTable': self.getDataTable(),
         'dataUsers': self.getDataUsers(),
         'namesList': self.getNamesList()}
        return info

    def getIsWinner(self):
        return False

    def getInBattle(self):
        return False

    def getIsInSquad(self):
        return False

    def getNamesList(self):
        return []

    def getDataTable(self):
        return self.getSquadDataTable() if self.getIsInSquad() else self.getSoloDataTable()

    def getDataUsers(self):
        return self.getSquadDataUsers() if self.getIsInSquad() else self.getSoloDataUsers()

    @staticmethod
    def getSoloDataTable():
        settings = getBattleRoyaleServerSettings()
        pointsChangesByPlace = settings.eventProgression.get('brPointsChangesByPlace', ())
        result = []
        isEmpty = not bool(len(pointsChangesByPlace))
        if isEmpty:
            return result
        maxCount, minCount = max(pointsChangesByPlace), min(pointsChangesByPlace)
        for i in range(maxCount, minCount - 1, -1):
            info = {'countChevrones': i,
             'count': pointsChangesByPlace.count(i)}
            if i == maxCount:
                info.update({'isWinner': True})
            result.append(info)

        return result

    @staticmethod
    def getSquadDataTable():
        settings = getBattleRoyaleServerSettings()
        pointsChangesByPlace = settings.eventProgression.get('brPointsChangesBySquadPlace', ())
        result = []
        squadCount = 3
        isEmpty = not bool(len(pointsChangesByPlace))
        if isEmpty:
            return result
        for idx, points in enumerate(pointsChangesByPlace, 1):
            info = {'countChevrones': points,
             'count': squadCount,
             'place': str(idx)}
            if idx == 1:
                info.update({'isWinner': True})
            result.append(info)

        return result

    def getSoloDataUsers(self):
        return []

    def getSquadDataUsers(self):
        return []


class PostBattleRoyaleScoreFormatter(BattleRoyaleScoreFormatter):

    def __init__(self, battleResultsVO):
        self.__battleResultsVO = battleResultsVO

    def getIsInSquad(self):
        return self.__battleResultsVO.get('common', {}).get('isInSquad', False)

    def getIsWinner(self):
        return self.__battleResultsVO.get('personal', {}).get('efficiency', {}).get('accPlace', False) == 1

    def getSoloDataUsers(self):
        teamInfo = self.__battleResultsVO.get('teams')
        if not teamInfo:
            return []
        result = []
        for playerInfo in teamInfo:
            place = playerInfo.get('place')
            playerData = {'userCurrent': playerInfo.get('isPersonal', False),
             'userName': playerInfo.get('nameLabel'),
             'userPlace': str(place),
             'isLeaver': playerInfo.get('isPrematureLeave'),
             'isWinner': place == 1}
            result.append(playerData)

        return result

    def getSquadDataUsers(self):
        teamInfo = self.__battleResultsVO.get('teams')
        if not teamInfo:
            return []
        result = []
        for idx, playerInfo in enumerate(teamInfo):
            place = playerInfo.get('place')
            playerData = {'userCurrent': playerInfo.get('isPersonal', False),
             'userName': playerInfo.get('nameLabel'),
             'isLeaver': playerInfo.get('isPrematureLeave'),
             'isWinner': place == 1}
            if idx % 3 == 1:
                playerData.update({'userPlace': str(place)})
            result.append(playerData)

        return result

    def getNamesList(self):
        personalName = self.__battleResultsVO.get('common', {}).get('playerFullNameStr', '')
        if not self.getIsInSquad():
            return [personalName]
        result = []
        for info in self.__battleResultsVO.get('teams', []):
            if info.get('isPersonalSquad', False):
                result.append(info.get('nameLabel', ''))

        return sorted(result)


class InBattleRoyaleScoreFormatter(BattleRoyaleScoreFormatter):

    def __init__(self, arenaDP):
        self._arenaDP = arenaDP
        self.placeFinder = createPlaceFinder(arenaDP)

    def getIsWinner(self):
        vInfoVO = self._arenaDP.getVehicleInfo()
        return SquadPlaceFinder.getPlace(vInfoVO, self._arenaDP) == 1 if self.getIsInSquad() else SoloPlaceFinder.getPlace(vInfoVO, self._arenaDP) == 1

    def getInBattle(self):
        return True

    def getIsInSquad(self):
        return self._arenaDP.getVehicleInfo().isSquadMan()

    def getSoloDataUsers(self):

        def soloSortedKey(items):
            vInfoVO, _ = items
            return SoloPlaceFinder.getPlace(vInfoVO, self._arenaDP)

        result = []
        for vInfoVO, _ in sorted(self._arenaDP.getVehiclesItemsGenerator(), key=soloSortedKey):
            userPlace = SoloPlaceFinder.getPlace(vInfoVO, self._arenaDP)
            playerData = {'userCurrent': vInfoVO.vehicleID == self._arenaDP.getPlayerVehicleID(),
             'userName': vInfoVO.player.name if vInfoVO.events.get('deathOrder', 0) else '',
             'userPlace': str(userPlace) if userPlace else '',
             'isWinner': userPlace == 1}
            result.append(playerData)

        return result

    def getSquadDataUsers(self):

        def squadSorteKey(items):
            vInfoVO, _ = items
            return (SquadPlaceFinder.getPlace(vInfoVO, self._arenaDP), SoloPlaceFinder.getPlace(vInfoVO, self._arenaDP))

        result = []
        playerWithPlaceIdx = 0
        for vInfoVO, _ in sorted(self._arenaDP.getVehiclesItemsGenerator(), key=squadSorteKey):
            teamPlace = SquadPlaceFinder.getPlace(vInfoVO, self._arenaDP)
            if teamPlace == 0:
                playerData = {'userCurrent': False,
                 'userName': '',
                 'isWinner': False}
            else:
                playerData = {'userCurrent': vInfoVO.vehicleID == self._arenaDP.getPlayerVehicleID(),
                 'userName': vInfoVO.player.name,
                 'isWinner': teamPlace == 1}
                if playerWithPlaceIdx % 3 == 1:
                    playerData.update({'userPlace': str(teamPlace)})
                playerWithPlaceIdx += 1
            result.append(playerData)

        return result

    def getNamesList(self):
        collection = vos_collections.AllyItemsCollection()
        if not self.getIsInSquad():
            return [self._arenaDP.getVehicleInfo().player.name]
        names = []
        for vInfoVO, _ in collection.iterator(self._arenaDP):
            if not vInfoVO.isObserver() and vInfoVO.isSquadMan():
                names.append(vInfoVO.player.name)

        return sorted(names)


class BattleRoyaleSummaryFormatter(object):

    @property
    def isInSquad(self):
        return False

    @property
    def inBattle(self):
        return False

    @property
    def isWinner(self):
        return False

    def getInfo(self):
        kwargs = self.getStaticInfo()
        kwargs.update({'statsList': self.getStatsList()})
        kwargs.update({'namesList': self.getNamesList()})
        kwargs.update({'rewardsList': self.getRewardsList()})
        return kwargs

    def getStaticInfo(self):
        return {'isInSquad': self.isInSquad,
         'inBattle': self.inBattle,
         'isWinner': self.isWinner}

    def getNamesList(self):
        return []

    def getRewardsList(self):
        return self._getRewardsInfo()

    def getStatsList(self):
        info = self._getStats()
        result = [self._getPlaceVO(info), self._getSimpleStatVO('chevrons', info)]
        if not self.inBattle:
            result.append(self._getSimpleStatVO('xp', info))
            result.append(self._getSeparator())
        result.append(self._getSimpleStatVO('kills', info))
        result.append(self._getSimpleStatVO('damageDealt', info))
        if self.isInSquad:
            result.append(self._getSimpleStatVO('squadKills', info))
        result.append(self._getSimpleStatVO('damageBlockedByArmor', info))
        return result

    def _getRewardsInfo(self):
        return []

    def _getStats(self):
        return {}

    def _getSimpleStatVO(self, label, efficiency):
        return {'image': self._getStatsImagesMap().get(label, self._getDefaultStatsImage()),
         'value': efficiency.get(label, 0),
         'tooltip': label}

    def _getPlaceVO(self, efficiency):
        totalValue = self._getTotalCount()
        return {'image': self._getStatsImagesMap().get('accPos', self._getDefaultStatsImage()),
         'value': efficiency.get('accPlace', 0),
         'totalValue': totalValue,
         'tooltip': 'accPos'}

    def _getSeparator(self):
        return {'image': self._getStatsImagesMap().get('separator', self._getDefaultStatsImage()),
         'value': 0,
         'tooltip': '',
         'isSeparator': True}

    def _getTotalCount(self):
        pass

    @classmethod
    def _getStatsImagesMap(cls):
        return {'accPos': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.place(),
         'chevrons': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.chevrons(),
         'xp': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.experience(),
         'kills': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.kills(),
         'damageDealt': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.dmg(),
         'criticalDamages': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.crits(),
         'damageBlockedByArmor': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.blocked(),
         'squadKills': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.killsSquad(),
         'separator': R.images.gui.maps.icons.battleRoyale.summaryResults.stats.separator()}

    @staticmethod
    def _getDefaultStatsImage():
        return R.images.gui.maps.icons.battleRoyale.summaryResults.stats.blocked()


class PostBattleRoyaleSummaryFormatter(BattleRoyaleSummaryFormatter):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, battleResultsVO):
        self.__battleResultsVO = battleResultsVO

    @property
    def isInSquad(self):
        return self.__battleResultsVO.get('common', {}).get('isInSquad', False)

    @property
    def isWinner(self):
        return self.__battleResultsVO.get('personal', {}).get('efficiency', {}).get('accPlace', 0) == 1

    def getNamesList(self):
        personalName = self.__battleResultsVO.get('common', {}).get('playerFullNameStr', '')
        if not self.isInSquad:
            return [personalName]
        result = []
        for info in self.__battleResultsVO.get('teams', []):
            if info.get('isPersonalSquad', False):
                result.append(info.get('nameLabel', ''))

        return sorted(result)

    def _getRewardsInfo(self):
        ids = self.__battleResultsVO.get('personal', {}).get('eventProgression', {}).get('questProgress', [])
        bonuses = []
        for qID in ids:
            quest = self.eventsCache.getQuestByID(qID)
            if quest:
                bonuses.extend(quest.getBonuses())

        return getRoyaleBonuses(mergeBonuses(bonuses))

    def _getStats(self):
        stats = {}
        personal = self.__battleResultsVO.get('personal', {})
        efficiency = personal.get('efficiency', {})
        stats.update(efficiency)
        stats.update(xp=personal.get('xp', 0))
        return stats

    def _getTotalCount(self):
        return len(set((vo.get('team', 0) for vo in self.__battleResultsVO.get('teams', [])))) if self.isInSquad else len(self.__battleResultsVO.get('teams', []))


class InBattleRoyaleSummaryFormatter(BattleRoyaleSummaryFormatter):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, arenaDP, efficiencyCtrl, bonusByQuestID=None):
        self._arenaDP = arenaDP
        self.__efficiencyCtrl = efficiencyCtrl
        self._bonusByQuestID = bonusByQuestID or {}
        self._totalEvents = {'damageDealt': _ETYPE.DAMAGE,
         'damageBlockedByArmor': _ETYPE.BLOCKED_DAMAGE}
        self.placeFinder = createPlaceFinder(arenaDP)

    @property
    def isInSquad(self):
        vInfoVO = self._arenaDP.getVehicleInfo()
        return vInfoVO.isSquadMan()

    @property
    def inBattle(self):
        return True

    @property
    def isWinner(self):
        vInfoVO = self._arenaDP.getVehicleInfo()
        return SquadPlaceFinder.getPlace(vInfoVO, self._arenaDP) == 1 if self.isInSquad else SoloPlaceFinder.getPlace(vInfoVO, self._arenaDP) == 1

    @property
    def chevronsDiff(self):
        vInfoVO = self._arenaDP.getVehicleInfo()
        position = self.placeFinder.getPlace(vInfoVO, self._arenaDP)
        return self._calculateChevrons(position)

    def getNamesList(self):
        collection = vos_collections.AllyItemsCollection()
        if not self.isInSquad:
            return [self._arenaDP.getVehicleInfo().player.name]
        names = []
        for vInfoVO, _ in collection.iterator(self._arenaDP):
            if not vInfoVO.isObserver() and vInfoVO.isSquadMan():
                names.append(vInfoVO.player.name)

        return sorted(names)

    def getStaticInfo(self):
        result = super(InBattleRoyaleSummaryFormatter, self).getStaticInfo()
        result.update({'chevronsDiff': self.chevronsDiff})
        return result

    def _getRewardsInfo(self):
        vInfoVO = self._arenaDP.getVehicleInfo()
        pos = self.placeFinder.getPlace(vInfoVO, self._arenaDP)
        return self._getAwardForPosition(pos)

    def _getAwardForPosition(self, pos):
        if self.isInSquad:
            template = battle_royale_common.BR_SQUAD_QUEST_FOR_POSITION_TEMPLATE
        else:
            template = battle_royale_common.BR_SOLO_QUEST_FOR_POSITION_TEMPLATE
        rewards = self._bonusByQuestID.get(template.format(position=pos), {})
        return getRoyaleBonusesFromDict(rewards)

    def _getStats(self):
        vStatsVO = self._arenaDP.getVehicleStats()
        vInfoVO = self._arenaDP.getVehicleInfo()
        result = {}
        efficiencyGetter = self.__efficiencyCtrl.getTotalEfficiency
        result.update({'kills': vStatsVO.frags})
        result.update({'damageDealt': efficiencyGetter(self._totalEvents.get('damageDealt'))})
        position = self.placeFinder.getPlace(vInfoVO, self._arenaDP)
        result.update({'accPlace': position})
        result.update({'chevrons': self._calculateChevrons(position)})
        result.update({'squadKills': self._getSquadKills()})
        result.update({'damageBlockedByArmor': efficiencyGetter(self._totalEvents.get('damageBlockedByArmor'))})
        return result

    def _calculateChevrons(self, pos):
        posIndex = max(0, pos - 1)
        settings = getBattleRoyaleServerSettings()
        if self.isInSquad:
            pointsChange = settings.eventProgression.get('brPointsChangesBySquadPlace', ())
        else:
            pointsChange = settings.eventProgression.get('brPointsChangesByPlace', ())
        return 0 if posIndex >= len(pointsChange) else pointsChange[posIndex]

    def _getSquadKills(self):
        if not self.isInSquad:
            return 0
        frags = 0
        collection = vos_collections.AllyItemsCollection()
        for vInfoVO, vStatsVO in collection.iterator(self._arenaDP):
            if not vInfoVO.isObserver() and vInfoVO.isSquadMan():
                frags += vStatsVO.frags

        return frags

    def _getTotalCount(self):
        return self.placeFinder.getTotalCount(self._arenaDP)


class PostBattleWidgetFormatter(object):
    __royaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, battleResultsVO):
        self.__battleResultsVO = battleResultsVO

    def getInfo(self):
        eventProgression = self.__battleResultsVO.get('personal').get('eventProgression', {})
        lastTitle = TitleData(*eventProgression.get('lastBRTitle', (0, 0)))
        lastMaxTitle = TitleData(*eventProgression.get('maxBRTitle', (0, 0)))
        currentTitle = TitleData(*eventProgression.get('accBRTitle', (0, 0)))
        result = {'lastTitleID': lastTitle[0],
         'lastMaxTitleID': lastMaxTitle[0],
         'currentTitleID': currentTitle[0],
         'titlesChain': self.__royaleController.getTitlesChainExt(currentTitle, lastTitle, lastMaxTitle)}
        return result


def getBattleRoyaleServerSettings():
    lobbyContext = dependency.instance(ILobbyContext)
    generalSettings = lobbyContext.getServerSettings().battleRoyale
    return generalSettings
