# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/constants.py
from bonus_constants import BonusName
from gui.shared.money import Currency
ZERO_TITLE_ID = 0
DEFAULT_REWARDS_COUNT = 7
ROYALE_POSTBATTLE_REWARDS_COUNT = 8
ROYALE_AWARDS_ORDER = ['battleToken',
 'items',
 'premium',
 'oneof',
 BonusName.FESTIVAL_ITEMS,
 Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL]
EQUIPMENT_ORDER = ['afterburning_battle_royale',
 'large_repairkit_battle_royale',
 'regenerationKit',
 'selfBuff',
 'bomber_battle_royale',
 'healPoint',
 'trappoint',
 'smoke_battle_royale']
VEHICLE_EQUIPMENTS = frozenset(['afterburning_battle_royale',
 'regenerationKit',
 'large_repairkit_battle_royale',
 'selfBuff'])
AVATAR_EQUIPMENTS = frozenset(['trappoint',
 'smoke_battle_royale',
 'bomber_battle_royale',
 'healPoint'])
BR_EQUIPMENTS_WITH_MESSAGES = frozenset(['trappoint',
 'afterburning_battle_royale',
 'regenerationKit',
 'selfBuff',
 'healPoint',
 'large_repairkit_battle_royale'])

class AmmoTypes(object):
    BASIC_SHELL = 'bshell'
    PREMIUM_SHELL = 'pshell'
    ITEM = 'item'


class BattleRoyalePerfProblems(object):
    HIGH_RISK = 'high_risk'
    MEDIUM_RISK = 'medium_risk'
    LOW_RISK = 'low_risk'


class ParamTypes(object):
    DELTA = 'delta'
    CONST = 'const'
    SIMPLE = 'simple'


BR_QUEST_ID_PREFIX = 'token:br:title'
BATTLE_ROYALE_VEHICLES_INVOICE = 'battle_royale_vehicles_invoice'
