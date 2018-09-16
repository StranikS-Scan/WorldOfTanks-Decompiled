# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/vos_collections.py
from gui.shared.sort_key import SortKey
from gui.battle_control.arena_info.arena_vos import EPIC_RANDOM_KEYS

class VehicleInfoSortKey(SortKey):
    __slots__ = ('vInfoVO', 'vStatsVO')

    def __init__(self, item):
        super(VehicleInfoSortKey, self).__init__()
        if hasattr(item, '__getitem__'):
            self.vInfoVO = item[0]
            self.vStatsVO = item[1]
        else:
            self.vInfoVO = item
            self.vStatsVO = None
        return

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        result = cmp(xvInfoVO.team, yvInfoVO.team)
        if result:
            return result
        result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
        if result:
            return result
        result = cmp(xvInfoVO.vehicleType, yvInfoVO.vehicleType)
        return result if result else cmp(xvInfoVO.player, yvInfoVO.player)


class SquadmanVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ('prebattleID',)

    def __init__(self, prebattleID, item):
        super(SquadmanVehicleInfoSortKey, self).__init__(item)
        self.prebattleID = prebattleID

    def _cmp(self, other):
        result = cmp(other.vInfoVO.isSquadMan(self.prebattleID), self.vInfoVO.isSquadMan(self.prebattleID))
        return result if result else super(SquadmanVehicleInfoSortKey, self)._cmp(other)


class SpawnGroupVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        result = cmp(self.vInfoVO.gameModeSpecific.getValue(EPIC_RANDOM_KEYS.PLAYER_GROUP), other.vInfoVO.gameModeSpecific.getValue(EPIC_RANDOM_KEYS.PLAYER_GROUP))
        return result if result else super(SpawnGroupVehicleInfoSortKey, self)._cmp(other)


class RankedVehicleInfoSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        result = cmp(other.vInfoVO.ranked.rank, self.vInfoVO.ranked.rank)
        return result if result else super(RankedVehicleInfoSortKey, self)._cmp(other)


class SquadmanSpawnGroupVehicleInfoSortKey(SpawnGroupVehicleInfoSortKey):
    __slots__ = ('prebattleID',)

    def __init__(self, prebattleID, item):
        super(SquadmanSpawnGroupVehicleInfoSortKey, self).__init__(item)
        self.prebattleID = prebattleID

    def _cmp(self, other):
        result = cmp(other.vInfoVO.isSquadMan(self.prebattleID), self.vInfoVO.isSquadMan(self.prebattleID))
        return result if result else super(SquadmanSpawnGroupVehicleInfoSortKey, self)._cmp(other)


class FragCorrelationSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
        return result if result else cmp(xvInfoVO.vehicleType.getOrderByClass(), yvInfoVO.vehicleType.getOrderByClass())


class RespawnSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        xvStatsVO = self.vStatsVO
        yvStatsVO = other.vStatsVO
        result = cmp(xvInfoVO.team, yvInfoVO.team)
        if result:
            return result
        result = cmp(xvStatsVO.stopRespawn, yvStatsVO.stopRespawn)
        if result:
            return result
        result = cmp(xvInfoVO.vehicleType, yvInfoVO.vehicleType)
        return result if result else cmp(xvInfoVO.player, yvInfoVO.player)


class RankSortKey(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        result = cmp(xvInfoVO.team, yvInfoVO.team)
        if result:
            return result
        result = cmp(yvInfoVO.isAlive(), xvInfoVO.isAlive())
        if result:
            return result
        result = cmp(yvInfoVO.ranked.rank, xvInfoVO.ranked.rank)
        if result:
            return result
        result = cmp(xvInfoVO.vehicleType, yvInfoVO.vehicleType)
        return result if result else cmp(xvInfoVO.player, yvInfoVO.player)


class _Collection(object):
    __slots__ = ('_sortKey',)

    def __init__(self, sortKey=None):
        super(_Collection, self).__init__()
        self._sortKey = sortKey

    def count(self, arenaDP):
        return len(self._buildSeq(arenaDP))

    def iterator(self, arenaDP):
        seq = self._buildSeq(arenaDP)
        seq = self._sortIfNeed(seq)
        for item in seq:
            yield item

    def ids(self, arenaDP):
        return map(self._getID, self.iterator(arenaDP))

    def _buildSeq(self, arenaDP):
        return arenaDP.getVehiclesInfoIterator()

    def _sortIfNeed(self, seq):
        if self._sortKey is not None:
            seq = sorted(seq, key=self._sortKey)
        return seq

    def _getID(self, item):
        return item.vehicleID


class VehiclesInfoCollection(_Collection):
    __slots__ = ()

    def _buildSeq(self, arenaDP):
        return arenaDP.getVehiclesInfoIterator()


class TeamVehiclesInfoCollection(_Collection):
    __slots__ = ('_team',)

    def __init__(self, team, sortKey=None):
        super(TeamVehiclesInfoCollection, self).__init__(sortKey=sortKey)
        self._team = team

    def _buildSeq(self, arenaDP):
        return [ item for item in arenaDP.getVehiclesInfoIterator() if item.team == self._team ]


class VehiclesItemsCollection(_Collection):
    __slots__ = ()

    def _buildSeq(self, arenaDP):
        return list(arenaDP.getVehiclesItemsGenerator())

    def _getID(self, item):
        return item[0].vehicleID


class AllyItemsCollection(VehiclesItemsCollection):
    __slots__ = ()

    def _buildSeq(self, arenaDP):
        seq = super(AllyItemsCollection, self)._buildSeq(arenaDP)
        teams = arenaDP.getAllyTeams()
        return [ item for item in seq if item[0].team in teams ]


class EnemyItemsCollection(VehiclesItemsCollection):
    __slots__ = ()

    def _buildSeq(self, arenaDP):
        seq = super(EnemyItemsCollection, self)._buildSeq(arenaDP)
        teams = arenaDP.getEnemyTeams()
        return [ item for item in seq if item[0].team in teams ]


class AliveItemsCollection(VehiclesItemsCollection):
    __slots__ = ('_collection',)

    def __init__(self, collection):
        super(AliveItemsCollection, self).__init__()
        self._collection = collection

    def _buildSeq(self, arenaDP):
        seq = self._collection.iterator(arenaDP)
        return [ item for item in seq if item[0].isAlive() ]
