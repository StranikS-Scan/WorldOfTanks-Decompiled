# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/constants.py
ROYALE_POSTBATTLE_REWARDS_COUNT = 8

class SteelHunterEquipmentNames(object):
    LARGE_REPAIRKIT = 'large_repairkit_battle_royale'
    AFTER_BURNING = 'afterburning_battle_royale'
    REGENERATION_KIT = 'regenerationKit'
    SELF_BUFF = 'selfBuff'
    TRAP_POINT = 'trappoint'
    REPAIR_POINT = 'repairpoint'
    HEAL_POINT = 'healPoint'
    SMOKE = 'smoke_battle_royale'
    BOMBER = 'arcade_bomber_battle_royale'
    KAMIKAZE = 'spawn_kamikaze'
    BERSERKER = 'berserker'
    MINE_FIELD = 'arcade_minefield_battle_royale'
    SMOKE_WITH_DAMAGE = 'arcade_smoke_battle_royale_with_damage'
    ARCADE_SMOKE = 'arcade_smoke_battle_royale'


BR_EQUIPMENTS_WITH_MESSAGES = frozenset([SteelHunterEquipmentNames.TRAP_POINT,
 SteelHunterEquipmentNames.AFTER_BURNING,
 SteelHunterEquipmentNames.REGENERATION_KIT,
 SteelHunterEquipmentNames.SELF_BUFF,
 SteelHunterEquipmentNames.HEAL_POINT,
 SteelHunterEquipmentNames.LARGE_REPAIRKIT,
 SteelHunterEquipmentNames.BERSERKER,
 SteelHunterEquipmentNames.MINE_FIELD,
 SteelHunterEquipmentNames.REPAIR_POINT,
 SteelHunterEquipmentNames.BOMBER,
 SteelHunterEquipmentNames.KAMIKAZE,
 SteelHunterEquipmentNames.SMOKE,
 SteelHunterEquipmentNames.SMOKE_WITH_DAMAGE,
 SteelHunterEquipmentNames.ARCADE_SMOKE])

class AmmoTypes(object):
    BASIC_SHELL = 'bshell'
    PREMIUM_SHELL = 'pshell'
    ITEM = 'item'
    CHARGE1 = 'charge1'
    CHARGE2 = 'charge2'
    CHARGE3 = 'charge3'
    CHARGE4 = 'charge4'
    CHARGES = (CHARGE1,
     CHARGE2,
     CHARGE3,
     CHARGE4)
    SHELLS = (BASIC_SHELL, PREMIUM_SHELL)


class BattleRoyalePerfProblems(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3


class ParamTypes(object):
    DELTA = 'delta'
    CONST = 'const'
    SIMPLE = 'simple'


BR_QUEST_ID_PREFIX = 'token:br:title'
BATTLE_ROYALE_VEHICLES_INVOICE = 'battle_royale_vehicles_invoice'
