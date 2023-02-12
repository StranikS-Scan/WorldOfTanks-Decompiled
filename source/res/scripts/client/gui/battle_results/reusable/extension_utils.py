# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/extension_utils.py
from enum import Enum
from constants import ARENA_BONUS_TYPE_IDS

class ReusableInfoFactory(object):

    class Keys(Enum):
        COMMON = 'common'
        AVATARS = 'avatars'
        AVATAR = 'avatar'
        PERSONAL = 'personal'
        PLAYERS = 'players'
        PLAYER = 'player'
        TEAM_BASES = 'teamBases'
        VEHICLE_DETAILED = 'vehicleDetailed'
        VEHICLE_SUMMARIZED = 'vehicleSummarized'
        VEHICLES = 'vehicles'
        FAIRPLAY_VIOLATIONS = 'fairplayViolations'
        SQUAD_BONUS = 'squadBonus'

    __default = {}
    __infoForBonusType = {}

    @classmethod
    def setDefaults(cls, defaults):
        cls.__default = defaults
        cls.__infoForBonusType = {key:{} for key in cls.__default.keys()}

    @classmethod
    def addForBonusType(cls, bonusType, key, infoCls):
        cls.__infoForBonusType[key][bonusType] = infoCls

    @classmethod
    def commonInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.COMMON)

    @classmethod
    def avatarsInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.AVATARS)

    @classmethod
    def avatarInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.AVATAR)

    @classmethod
    def personalInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.PERSONAL)

    @classmethod
    def playerInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.PLAYER)

    @classmethod
    def playersInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.PLAYERS)

    @classmethod
    def teamBasesInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.TEAM_BASES)

    @classmethod
    def vehicleDetailedInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.VEHICLE_DETAILED)

    @classmethod
    def vehicleSummarizeInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.VEHICLE_SUMMARIZED)

    @classmethod
    def vehiclesInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.VEHICLES)

    @classmethod
    def fairplayViolationForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.FAIRPLAY_VIOLATIONS)

    @classmethod
    def squadBonusInfoForBonusType(cls, bonusType):
        return cls.__getForBonusType(bonusType, cls.Keys.SQUAD_BONUS)

    @classmethod
    def __getForBonusType(cls, bonusType, key):
        return cls.__infoForBonusType[key].get(bonusType, cls.__default[key])
