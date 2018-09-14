# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/stronghold_items.py
import itertools
from helpers.time_utils import ONE_MINUTE, ONE_HOUR
from collections import namedtuple
BYTTLETYPE_SORTIE = u'SORTIE'
AIRSTRIKE = 'AIRSTRIKE'
ARTILLERY_STRIKE = 'ARTILLERY_STRIKE'
REQUISITION = 'REQUISITION'
HIGH_CAPACITY_TRANSPORT = 'HIGH_CAPACITY_TRANSPORT'
SUPPORT_TYPE = 'SUPPORT'
REQUISITION_TYPE = 'REQUISITION'
HEAVYTRUCKS_TYPE = 'HEAVYTRUCKS'
RESERVE_STRONGHOLD_ORDER = (SUPPORT_TYPE, HEAVYTRUCKS_TYPE, REQUISITION_TYPE)
RESERVE_SORTIE_ORDER = (SUPPORT_TYPE, HEAVYTRUCKS_TYPE)
SUPPORT_ORDER = (AIRSTRIKE, ARTILLERY_STRIKE)
RESERVE_ITEMS = {SUPPORT_TYPE: (AIRSTRIKE, ARTILLERY_STRIKE),
 REQUISITION_TYPE: (REQUISITION,),
 HEAVYTRUCKS_TYPE: (HIGH_CAPACITY_TRANSPORT,)}

def isEnemyBattleIndex(index):
    return index >= 3


class StrongholdSettings(namedtuple('StrongholdSettings', ['type',
 'min_level',
 'max_level',
 'min_players_count',
 'max_players_count',
 'industrial_resource_multiplier',
 'max_legionaries_count',
 'public',
 'battle_duration',
 'battle_series_duration',
 'battle_idx',
 'matchmaker_next_tick',
 'time_to_ready',
 'direction',
 'requisition_bonus_percent',
 'enemy_clan',
 'clan',
 'available_reserves',
 'permissions',
 'ready_button_enabled',
 'selected_reserves',
 'battle_series_status',
 'battles_end_time',
 'battles_start_time',
 'fort_battles_before_start_lag',
 'sorties_before_start_lag',
 'sorties_before_end_lag'])):
    """
    Stronghold data model
    
    more info
    https://confluence.wargaming.net/display/WEBDEV/WGSH+-+API+for+WoT+client+dialogs#WGSH-APIforWoTclientdialogs-Prebattledialog
    """

    def __init__(self, **kwargs):
        super(StrongholdSettings, self).__init__(**kwargs)
        self.__enemyClan = ClanData(**self.enemy_clan) if self.enemy_clan else None
        self.__clan = ClanData(**self.clan) if self.clan else None
        self.__availableReserves = {group:[ ReserveItem(**v) for v in groupvalues ] for group, groupvalues in self.available_reserves.iteritems()}
        self.__battleSeriesStatus = [ BattleSeriesItem(index=index, **v) for index, v in enumerate(self.battle_series_status) ]
        self.__currentBattle = None
        for bs in self.__battleSeriesStatus:
            if bs.getCurrentBattle():
                self.__currentBattle = bs

        self.__selectedReserves = [ self.getReserveById(reserveId) for reserveId in self.selected_reserves ]
        self.__reserveOrder = RESERVE_SORTIE_ORDER if self.isSortie() else RESERVE_STRONGHOLD_ORDER
        self.__readyButtonEnabled = self.ready_button_enabled
        return

    def isSortie(self):
        """
            :return: is sortie battle type
        """
        return self.type == BYTTLETYPE_SORTIE

    def getMinLevel(self):
        """
            :return: vehicle min level
        """
        return self.min_level

    def getMaxLevel(self):
        """
            :return: vehicle max level
        """
        return self.max_level

    def getMinPlayerCount(self):
        """
            :return: min players count
        """
        return self.min_players_count

    def getMaxPlayerCount(self):
        """
            :return: max players count
        """
        return self.max_players_count

    def getResourceMultiplier(self):
        """
            :return: first battle of the day bonus
        """
        return self.industrial_resource_multiplier

    def getMaxLegCount(self):
        """
            :return: max legionaries count
        """
        return self.max_legionaries_count

    def getPublic(self):
        """
            :return: unit visible status for legionaries
        """
        return self.public

    def getBattleDurationMinuts(self):
        """
            :return: battle duration in minuts
        """
        return self.battle_duration / ONE_MINUTE

    def getBattleSeriesDurationMinuts(self):
        """
            :return: battle series duration in minuts
        """
        return self.battle_series_duration / ONE_MINUTE

    def getBattleSeriesDurationHours(self):
        """
            :return: battle series duration in hours
        """
        return self.battle_series_duration / ONE_HOUR

    def getMatchmakerNextTick(self):
        """
            :return: matchmaker next tick
        """
        return self.matchmaker_next_tick

    def getChainMatchmakerNextTick(self):
        """
            :return: matchmaker next tick for next battle in chain
        """
        return self.time_to_ready

    def getBattlesStartTime(self):
        """
            :return: battles start time
        """
        return self.battles_start_time

    def getBattlesEndTime(self):
        """
            :return: battles end time
        """
        return self.battles_end_time

    def getFortBattlesBeforeStartLag(self):
        """
            :return: fort battles before start lag
        """
        return self.fort_battles_before_start_lag

    def getSortiesBeforeStartLag(self):
        """
            :return: sorties before start lag
        """
        return self.sorties_before_start_lag

    def getSortiesBeforeEndLag(self):
        """
            :return: sorties before end lag
        """
        return self.sorties_before_end_lag

    def getDirection(self):
        """
            :return: direction of the battle: 'A', 'B', 'C', 'D'
        """
        return self.direction

    def getRequisitionBonusPercent(self):
        """
            :return: bonus from requisition
        """
        return self.requisition_bonus_percent

    def getPermissions(self):
        """
            :return: player permitions
        """
        return self.permissions

    def getSelectedReservesIdx(self):
        """
            :return: selected reserves
        """
        return self.selected_reserves

    def getAvailableReserves(self):
        """
            :return: all available reserves. See ReserveItem
        """
        return self.__availableReserves

    def getClan(self):
        """
            :return: clan data. See ClanData
        """
        return self.__clan

    def getEnemyClan(self):
        """
            :return: enemy clan data. See ClanData
        """
        return self.__enemyClan

    def getBattleSeriesStatus(self):
        """
            :return: battle series data. See BattleSeriesItem
        """
        return self.__battleSeriesStatus

    def getSelectedReserves(self):
        """
            :return: selected reserves. See ReserveItem
        """
        return self.__selectedReserves

    def getCurrentBattle(self):
        """
            :return: current battle and index. See BattleSeriesItem
        """
        return self.__currentBattle

    def isFirstBattle(self):
        """
            :return: is first battle
        """
        return self.__currentBattle is None

    def getBattleIdx(self):
        """
            :return: battle index
        """
        return self.battle_idx

    def getReserveOrder(self):
        """
            :return: reserve order
        """
        return RESERVE_SORTIE_ORDER if self.isSortie() else RESERVE_STRONGHOLD_ORDER

    def getReserveById(self, reserveId):
        """
            :return: find reserve by id
        """
        if id is None:
            return
        else:
            availableReserves = self.getAvailableReserves()
            for reserve in itertools.chain(*availableReserves.itervalues()):
                if reserve.getId() == reserveId:
                    return reserve

            return

    def getUniqueReservesByGroupType(self, groupType):
        """
            :return: unique and sorted reserves by choosen type
        """
        reserves = []
        availableReserves = self.getAvailableReserves()
        for type in RESERVE_ITEMS[groupType]:
            reserves.extend(availableReserves[type])

        unique = []
        for reserve in self.getSelectedReserves():
            if reserve and reserve.getGroupType() == groupType:
                unique.append(reserve)

        for item in reserves:
            if item not in unique:
                unique.append(item)

        uniqueAndSorted = sorted(unique, cmp=lambda x, y: x.__cmp__(y))
        return uniqueAndSorted

    def getReserveCount(self, type, level):
        """
            :return: reserves count by type and level
        """
        count = 0
        availableReserves = self.getAvailableReserves()
        for reserve in itertools.chain(*availableReserves.itervalues()):
            if reserve.type == type and reserve.level == level:
                count += 1

        return count

    def getReadyButtonEnabled(self):
        """
            :return: return ready button enable
        """
        return self.__readyButtonEnabled


class ReserveItem(namedtuple('ReserveItem', ['id',
 'type',
 'level',
 'bonus_percent',
 'title',
 'description',
 'production_elapsed'])):
    """
    Reserve data model
    """

    def getId(self):
        """
            :return: reserve id
        """
        return self.id

    def getType(self):
        """
            :return: reserve type
        """
        return self.type

    def getGroupType(self):
        """
            :return: reserve group type
        """
        for groupType, group in RESERVE_ITEMS.iteritems():
            if self.type in group:
                return groupType

    def getLevel(self):
        """
            :return: reserve level
        """
        return self.level

    def getBonusPercent(self):
        """
            :return: reserve bonus percent
        """
        return self.bonus_percent

    def getDescription(self):
        """
            :return: reserve description
        """
        return self.description

    def getTitle(self):
        """
            :return: reserve title
        """
        return self.title

    def getProductionElapsed(self):
        """
            :return: production elapsed
        """
        return self.production_elapsed

    def isRequsition(self):
        """
            :return: reserve is requisition
        """
        return self.getGroupType() == REQUISITION

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.type == other.type and self.level == other.level
        else:
            return False

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        group = RESERVE_ITEMS[self.getGroupType()]
        typeOrder1 = group.index(self.type)
        typeOrder2 = group.index(other.type)
        return cmp((other.level, typeOrder1), (self.level, typeOrder2))

    def __getGroupType(self):
        for groupType, group in RESERVE_ITEMS.iteritems():
            if self.type in group:
                return groupType


class BattleSeriesItem(namedtuple('BattleSeriesItem', ['index',
 'clan_owner_id',
 'map_id',
 'geometry_id',
 'gameplay_id',
 'first_resp_clan_id',
 'second_resp_clan_id',
 'battle_reward',
 'current_battle',
 'attacker'])):
    """
        Battle series data model
    """

    def getIndex(self):
        return self.index

    def getClanId(self):
        """
            :return: clan id
        """
        return self.clan_owner_id

    def getMapId(self):
        """
            :return: map id
        """
        return self.map_id

    def getGeometryId(self):
        """
            :return: geometry id
        """
        return self.geometry_id

    def getGameplayId(self):
        """
            :return: gameplay id
        """
        return self.gameplay_id

    def getFirstClanId(self):
        """
            :return: clan id on first (green) spawn point
        """
        return self.first_resp_clan_id

    def getBattleReward(self):
        """
            :return: reward for battle
        """
        return self.battle_reward

    def getCurrentBattle(self):
        """
            :return: is this battle current
        """
        return self.current_battle

    def getAttacker(self):
        """
            :return: attack or defence. For current battle only
        """
        return self.attacker


class ClanData(namedtuple('ClanData', ['id',
 'tag',
 'name',
 'status_ready',
 'color'])):
    """
        Clan data model
    """

    def getId(self):
        return self.id

    def getTag(self):
        return self.tag

    def getName(self):
        return self.name

    def getColor(self):
        return self.color

    def getReadyStatus(self):
        return self.status_ready


class StrongholdDataDiffer(object):
    """
        Class that make diff for update stronghold data
    """

    def __init__(self):
        self._data = None
        return

    def makeDiff(self, data):
        diff = set()
        if data is not None:
            if self._data is None:
                diff.add('update_all')
            else:
                for k, v in data.iteritems():
                    if cmp(self._data.get(k), v):
                        diff.add(k)

        self._data = data
        return diff
