# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/currency_records_item_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_details_model import CurrencyRecordsItemDetailsModel

class CurrencyRecordsItemModel(ViewModel):
    __slots__ = ()
    CRYSTAL = 'crystal'
    XP_COST = 'xp'
    FREE_XP = 'freeXP'
    CREDITS = 'credits'
    GOLD = 'gold'
    COMMON_CURRENCY = 'commonCurrency'
    ORIGINAL_CRYSTALS = 'originalCrystals'
    EVENT_CRYSTALS = 'eventCrystals'
    AUTO_EQUIP_CRYSTALS = 'autoEquipCrystals'
    TOTAL_CRYSTALS = 'totalCrystals'
    ORIGINAL_XP = 'originalXP'
    ACHIEVEMENT_XP = 'achievementXP'
    FRIENDLY_FIRE_PENALTY_XP = 'originalXPPenalty'
    IGR_BONUS_XP = 'igrBonusXP'
    FIRST_WIN_XP = 'firstWinXP'
    ADDITIONAL_BONUS_XP = 'additionalBonusXP'
    BOOSTERS_XP = 'boostersXP'
    TACTICAL_TRAINING_XP = 'tacticalTrainingXP'
    EVENT_XP = 'eventXP'
    REFERRAL_BONUS_XP = 'referralBonusXP'
    PREMIUM_VEHICLE_XP = 'premiumVehicleXP'
    SQUAD_BONUS_XP = 'squadBonusXP'
    SQUAD_PENALTY_XP = 'squadPenaltyXP'
    WOT_PLUS_BONUS_XP = 'wotPlusBonusXP'
    TOTAL_XP = 'totalXP'
    ORIGINAL_FREE_XP = 'originalFreeXP'
    ACHIEVEMENT_FREE_XP = 'achievementFreeXP'
    IGR_BONUS_FREE_XP = 'igrBonusFreeXP'
    FIRST_WIN_FREE_XP = 'firstWinFreeXP'
    ADDITIONAL_BONUS_FREE_XP = 'additionalBonusFreeXP'
    BOOSTERS_FREE_XP = 'boostersFreeXP'
    MILITARY_MANEUVERS_FREE_XP = 'militaryManeuversFreeXP'
    EVENT_FREE_XP = 'eventFreeXP'
    PREMIUM_VEHICLE_FREE_XP = 'premiumVehicleFreeXP'
    WOT_PLUS_BONUS_FREE_XP = 'wotPlusBonusFreeXP'
    TOTAL_FREE_XP = 'totalFreeXP'
    BASE_EARNED_CREDITS = 'baseEarnedCredits'
    SQUAD_BONUS_CREDITS = 'squadBonusCredits'
    ACHIEVEMENT_CREDITS = 'achievementCredits'
    BOOSTERS_CREDITS = 'boostersCredits'
    BATTLE_PAYMENTS_CREDITS = 'battlePaymentsCredits'
    EVENT_PAYMENTS_CREDITS = 'eventPaymentsCredits'
    REFERRAL_BONUS_CREDITS = 'referralBonusCredits'
    WOT_PLUS_BONUS_CREDITS = 'wotPlusBonusCredits'
    FRIENDLY_FIRE_PENALTY_CREDITS = 'friendlyFirePenaltyCredits'
    FRIENDLY_FIRE_COMPENSATION_CREDITS = 'friendlyFireCompensationCredits'
    PIGGY_BANK_CREDITS = 'piggyBankCredits'
    AUTO_REPAIR_CREDITS = 'autoRepairCredits'
    AUTO_LOAD_CREDITS = 'autoLoadCredits'
    AUTO_EQUIP_CREDITS = 'autoEquipCredits'
    INTERMEDIATE_TOTAL_CREDITS = 'intermediateTotalCredits'
    TOTAL_CREDITS = 'totalCredits'
    GOLD_EVENT_PAYMENTS = 'goldEventPayments'
    GOLD_PIGGY_BANK = 'goldPiggyBank'
    INTERMEDIATE_TOTAL_GOLD = 'intermediateTotalGold'
    TOTAL_GOLD = 'totalGold'
    AOGAS_FACTOR = 'aogasFactor'
    DESERTER_VIOLATION = 'deserterViolation'
    AFK_VIOLATION = 'afkViolation'
    SUICIDE_VIOLATION = 'suicideViolation'

    def __init__(self, properties=5, commands=0):
        super(CurrencyRecordsItemModel, self).__init__(properties=properties, commands=commands)

    def getParamName(self):
        return self._getString(0)

    def setParamName(self, value):
        self._setString(0, value)

    def getCurrencyType(self):
        return self._getString(1)

    def setCurrencyType(self, value):
        self._setString(1, value)

    def getBaseValue(self):
        return self._getReal(2)

    def setBaseValue(self, value):
        self._setReal(2, value)

    def getPremiumValue(self):
        return self._getReal(3)

    def setPremiumValue(self, value):
        self._setReal(3, value)

    def getDetailedItemRecords(self):
        return self._getArray(4)

    def setDetailedItemRecords(self, value):
        self._setArray(4, value)

    @staticmethod
    def getDetailedItemRecordsType():
        return CurrencyRecordsItemDetailsModel

    def _initialize(self):
        super(CurrencyRecordsItemModel, self)._initialize()
        self._addStringProperty('paramName', '')
        self._addStringProperty('currencyType', '')
        self._addRealProperty('baseValue', 0.0)
        self._addRealProperty('premiumValue', 0.0)
        self._addArrayProperty('detailedItemRecords', Array())
