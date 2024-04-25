# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/reusable.py
from account_shared import getFairPlayViolationName
from constants import FAIRPLAY_VIOLATIONS
from gui.battle_results.reusable import ReusableInfoFactory
from gui.battle_results.reusable.shared import VehicleDetailedInfo, no_key_error
from gui.battle_results.reusable.shared import VehicleSummarizeInfo
from gui.battle_results.reusable.vehicles import VehiclesInfo
from gui.battle_results.reusable.avatars import AvatarInfo
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType

class HBVehicleDetailedInfo(VehicleDetailedInfo):
    __slots__ = ('_frontmanRoleID',)

    def __init__(self, *args, **kwargs):
        super(HBVehicleDetailedInfo, self).__init__(*args, **kwargs)
        self._frontmanRoleID = 0

    @property
    def frontmanRoleID(self):
        return self._frontmanRoleID

    @classmethod
    @no_key_error
    def makeForVehicle(cls, vehicleID, vehicle, player, vehicleRecords, critsRecords=None):
        info = super(HBVehicleDetailedInfo, cls).makeForVehicle(vehicleID, vehicle, player, vehicleRecords, critsRecords, instanceCls=cls)
        info._frontmanRoleID = vehicleRecords['frontmanRoleID']
        return info


class HBVehicleSummarizeInfo(VehicleSummarizeInfo):

    @property
    def frontmanRoleID(self):
        return self._findFirstNoZero('frontmanRoleID')


class HBAvatarInfo(AvatarInfo):
    __slots__ = ('__violationName', '__isBanned')

    def __init__(self, bonusType, totalDamaged=0, avatarKills=0, avatarDamaged=0, avatarDamageDealt=0, fairplayViolations=None, wasInBattle=True, accRank=None, prevAccRank=None, badges=(), **kwargs):
        super(HBAvatarInfo, self).__init__(bonusType, totalDamaged, avatarKills, avatarDamaged, avatarDamageDealt, fairplayViolations, wasInBattle, accRank, prevAccRank, badges, **kwargs)
        _, penalties, violations = fairplayViolations
        self.__violationName = getFairPlayViolationName(penalties if penalties != 0 else violations)
        self.__isBanned = penalties != 0

    @property
    def modelViolationName(self):
        if self.__isBanned:
            return TeamMemberBanType.BANNED
        return TeamMemberBanType.WARNED if self.__violationName in (FAIRPLAY_VIOLATIONS.HB_AFK, FAIRPLAY_VIOLATIONS.HB_DESERTER) else TeamMemberBanType.NOTBANNED


class HBVehiclesInfo(VehiclesInfo):
    _VEHICLE_DETAILED_INFO_CLS = HBVehicleDetailedInfo
    _VEHICLE_SUMMARIZE_INFO_CLS = HBVehicleSummarizeInfo


for arenaBonusType in ARENA_BONUS_TYPE.HB_RANGE:
    ReusableInfoFactory.setVehicleDetailedInfoForBonusType(arenaBonusType, HBVehicleDetailedInfo)
    ReusableInfoFactory.setVehicleSummarizeInfoForBonusType(arenaBonusType, HBVehicleSummarizeInfo)
    ReusableInfoFactory.setVehiclesInfoForBonusType(arenaBonusType, HBVehiclesInfo)
    ReusableInfoFactory.setAvatarInfoForBonusType(arenaBonusType, HBAvatarInfo)
