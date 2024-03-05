# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/mission_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BonusIconEnum(Enum):
    BATTLE_BONUS_X5_CN = 'battle_bonus_x5.CN'
    BATTLE_BONUS_X5 = 'battle_bonus_x5'
    BATTLEBOOSTER_OVERLAY = 'battleBooster_overlay'
    BATTLEBOOSTERREPLACE_OVERLAY = 'battleBoosterReplace_overlay'
    BERTHS = 'berths'
    BOOSTER_CREDITS_PREMIUM = 'booster_credits_premium'
    BOOSTER_CREDITS = 'booster_credits'
    BOOSTER_CREW_XP = 'booster_crew_xp'
    BOOSTER_FL_XP = 'booster_fl_xp'
    BOOSTER_FREE_XP_AND_CREW_XP_PREMIUM = 'booster_free_xp_and_crew_xp_premium'
    BOOSTER_FREE_XP_AND_CREW_XP = 'booster_free_xp_and_crew_xp'
    BOOSTER_FREE_XP = 'booster_free_xp'
    BOOSTER_XP_PREMIUM = 'booster_xp_premium'
    BOOSTER_XP = 'booster_xp'
    COATEDOPTICS = 'coatedOptics'
    COMMANDER_SIXTHSENSE = 'commander_sixthSense'
    COMMON = 'common'
    CREDITS = 'credits'
    DRIVER_SMOOTHDRIVING = 'driver_smoothDriving'
    EMBLEM = 'emblem'
    ENHANCEDAIMDRIVES = 'enhancedAimDrives'
    EQUIPMENTMODERNIZED_1_OVERLAY = 'equipmentModernized_1_overlay'
    EQUIPMENTMODERNIZED_2_OVERLAY = 'equipmentModernized_2_overlay'
    EQUIPMENTMODERNIZED_3_OVERLAY = 'equipmentModernized_3_overlay'
    EQUIPMENTPLUS_OVERLAY = 'equipmentPlus_overlay'
    EQUIPMENTTROPHYBASIC_OVERLAY = 'equipmentTrophyBasic_overlay'
    EQUIPMENTTROPHYUPGRADED_OVERLAY = 'equipmentTrophyUpgraded_overlay'
    EXTRAHEALTHRESERVE = 'extraHealthReserve'
    FIREFIGHTING = 'fireFighting'
    FREEXP = 'freeXP'
    GOLD = 'gold'
    GUNNER_SMOOTHTURRET = 'gunner_smoothTurret'
    HANDEXTINGUISHERS = 'handExtinguishers'
    LARGEMEDKIT = 'largeMedkit'
    LARGEREPAIRKIT = 'largeRepairkit'
    NATURALCOVER = 'naturalCover'
    PREMIUM_PLUS_1 = 'premium_plus_1'
    PREMIUM_PLUS_14 = 'premium_plus_14'
    RAMMER = 'rammer'
    SLOTS = 'slots'
    SMALLMEDKIT = 'smallMedkit'
    SMALLREPAIRKIT = 'smallRepairkit'
    TANKMEN = 'tankmen'
    TIMER = 'timer'


class MissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MissionModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getCurrentProgression(self):
        return self._getNumber(2)

    def setCurrentProgression(self, value):
        self._setNumber(2, value)

    def getProgressionTotal(self):
        return self._getNumber(3)

    def setProgressionTotal(self, value):
        self._setNumber(3, value)

    def getIcon(self):
        return BonusIconEnum(self._getString(4))

    def setIcon(self, value):
        self._setString(4, value.value)

    def getMarsPoints(self):
        return self._getNumber(5)

    def setMarsPoints(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(MissionModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('currentProgression', 0)
        self._addNumberProperty('progressionTotal', 0)
        self._addStringProperty('icon')
        self._addNumberProperty('marsPoints', 0)
