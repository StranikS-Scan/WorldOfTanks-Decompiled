# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/reusable.py
from account_shared import getFairPlayViolationName
from constants import FAIRPLAY_VIOLATIONS
from gui.battle_results.reusable import ReusableInfoFactory
from gui.battle_results.reusable.avatars import AvatarInfo
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType

class HBAvatarInfo(AvatarInfo):
    __slots__ = ('__violationName', '__isBanned', '__divisionLevel')

    def __init__(self, bonusType, totalDamaged=0, avatarKills=0, avatarDamaged=0, avatarDamageDealt=0, fairplayViolations=None, wasInBattle=True, accRank=None, prevAccRank=None, badges=(), divisionLevel=1, **kwargs):
        super(HBAvatarInfo, self).__init__(bonusType, totalDamaged, avatarKills, avatarDamaged, avatarDamageDealt, fairplayViolations, wasInBattle, accRank, prevAccRank, badges, **kwargs)
        _, penalties, violations = fairplayViolations
        self.__violationName = getFairPlayViolationName(penalties if penalties != 0 else violations)
        self.__isBanned = penalties != 0
        self.__divisionLevel = divisionLevel

    @property
    def modelViolationName(self):
        if self.__isBanned:
            return TeamMemberBanType.BANNED
        return TeamMemberBanType.WARNED if self.__violationName in (FAIRPLAY_VIOLATIONS.HB_AFK, FAIRPLAY_VIOLATIONS.HB_DESERTER) else TeamMemberBanType.NOTBANNED

    @property
    def divisionLevel(self):
        return self.__divisionLevel


for arenaBonusType in ARENA_BONUS_TYPE.HB_RANGE:
    ReusableInfoFactory.setAvatarInfoForBonusType(arenaBonusType, HBAvatarInfo)
