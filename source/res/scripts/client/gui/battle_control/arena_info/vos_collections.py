# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/vos_collections.py
from collections import defaultdict

class _SortKey(object):
    __slots__ = ()

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __hash__(self):
        raise TypeError('hash not implemented')

    def _cmp(self, other):
        raise NotImplementedError


class VehicleInfoSortKey(_SortKey):
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


class Mark1EventSort(VehicleInfoSortKey):
    __slots__ = ()

    def _cmp(self, other):
        xvInfoVO = self.vInfoVO
        yvInfoVO = other.vInfoVO
        return cmp(xvInfoVO.player, yvInfoVO.player)


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


class _WinPointsSortKey(_SortKey):
    __slots__ = ('teamWinPoints', 'internal')

    def __init__(self, item, *args):
        super(_WinPointsSortKey, self).__init__()
        assert len(item) > 2, 'Given key is used in the FalloutMultiTeamItemsCollection only'
        self.internal = self._createInternal(item[:2])
        self.teamWinPoints = item[2]

    def _cmp(self, other):
        result = cmp(other.teamWinPoints, self.teamWinPoints)
        if result:
            return result
        else:
            return cmp(self.internal, other.internal)

    @classmethod
    def _createInternal(cls, item):
        raise NotImplementedError


class WinPointsAndVehicleInfoSortKey(_WinPointsSortKey):

    @classmethod
    def _createInternal(cls, item):
        return VehicleInfoSortKey(item)


class WinPointsAndRespawnSortKey(_WinPointsSortKey):

    @classmethod
    def _createInternal(cls, item):
        return RespawnSortKey(item)


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

    def _buildSeq(self, arenaDP):
        return arenaDP.getVehiclesInfoIterator()


class TeamVehiclesInfoCollection(_Collection):
    __slots__ = ('_team',)

    def __init__(self, team, sortKey=None):
        super(TeamVehiclesInfoCollection, self).__init__(sortKey=sortKey)
        self._team = team

    def _buildSeq(self, arenaDP):
        return filter(lambda item: item.team == self._team, arenaDP.getVehiclesInfoIterator())


class VehiclesItemsCollection(_Collection):

    def _buildSeq(self, arenaDP):
        return list(arenaDP.getVehiclesItemsGenerator())

    def _getID(self, item):
        return item[0].vehicleID


class AllyItemsCollection(VehiclesItemsCollection):

    def _buildSeq(self, arenaDP):
        seq = super(AllyItemsCollection, self)._buildSeq(arenaDP)
        teams = arenaDP.getAllyTeams()
        return filter(lambda (vInfo, _): vInfo.team in teams, seq)


class EnemyItemsCollection(VehiclesItemsCollection):

    def _buildSeq(self, arenaDP):
        seq = super(EnemyItemsCollection, self)._buildSeq(arenaDP)
        teams = arenaDP.getEnemyTeams()
        return filter(lambda (vInfo, _): vInfo.team in teams, seq)


class FalloutMultiTeamItemsCollection(VehiclesItemsCollection):

    def _sortIfNeed(self, seq):
        if self._sortKey is not None:
            teamsStats = defaultdict(int)
            buffer_ = list(seq)
            for vInfo, vStats in buffer_:
                teamsStats[vInfo.team] += vStats.winPoints

            seq = []
            for vInfo, vStats in buffer_:
                seq.append((vInfo, vStats, teamsStats[vInfo.team]))

            seq = map(lambda (info, stats, _): (info, stats), sorted(seq, key=self._sortKey))
        return seq
