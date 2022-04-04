# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/vos_collections.py
from RTSShared import RTSSupply
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey, VehiclesInfoCollection
from gui.shared.sort_key import SortKey
from gui.battle_control.arena_info.arena_vos import RtsKeys

class RTSVehicleInfoSortKey(VehicleInfoSortKey):

    def _cmp(self, other):
        selfInfoVO = self.vInfoVO
        otherInfoVO = other.vInfoVO
        if avatar_getter.isCommanderCtrlMode():
            result = cmp(selfInfoVO.gameModeSpecific.getValue(RtsKeys.VEHICLE_GROUP), otherInfoVO.gameModeSpecific.getValue(RtsKeys.VEHICLE_GROUP))
            if result:
                return result
        return super(RTSVehicleInfoSortKey, self)._cmp(other)


class SupplySortKey(SortKey):
    __slots__ = ('supplyInfo',)

    def __init__(self, supplyInfo):
        super(SupplySortKey, self).__init__()
        self.supplyInfo = supplyInfo

    def _cmp(self, other):
        return cmp(self.supplyInfo, other.supplyInfo)


class SupplyInfoCollection(VehiclesInfoCollection):
    __slots__ = ('_filterID', '_isAlly')

    def __init__(self, sortKey=None, isAlly=True):
        super(SupplyInfoCollection, self).__init__(sortKey)
        self._isAlly = isAlly

    def _buildSeq(self, arenaDP):
        for vo in super(SupplyInfoCollection, self)._buildSeq(arenaDP):
            if vo.isSupply() and arenaDP.isAllyTeam(vo.team) == self._isAlly:
                yield vo

    def _getID(self, item):
        return RTSSupply.getID(item.vehicleType)
