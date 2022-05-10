# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/constants.py
ROYALE_POSTBATTLE_REWARDS_COUNT = 8

class BattleRoyaleEquipments(object):
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
    FIRE_CIRCLE = 'fireCircle'
    CORRODING_SHOT = 'corrodingShot'
    CLING_BRANDER = 'clingBrander'
    ADAPTATION_HEALTH_RESTORE = 'adaptationHealthRestore'
    THUNDER_STRIKE = 'thunderStrike'
    SHOT_PASSION = 'shotPassion'


class BattleRoyaleComponents(object):
    SHOT_PASSION = 'shotPassionComponent'
    FIRE_CIRCLE = 'vehicleFireCircleEffectComponent'


BR_EQUIPMENTS_WITH_MESSAGES = frozenset([BattleRoyaleEquipments.TRAP_POINT,
 BattleRoyaleEquipments.AFTER_BURNING,
 BattleRoyaleEquipments.REGENERATION_KIT,
 BattleRoyaleEquipments.SELF_BUFF,
 BattleRoyaleEquipments.HEAL_POINT,
 BattleRoyaleEquipments.LARGE_REPAIRKIT,
 BattleRoyaleEquipments.BERSERKER,
 BattleRoyaleEquipments.MINE_FIELD,
 BattleRoyaleEquipments.REPAIR_POINT,
 BattleRoyaleEquipments.BOMBER,
 BattleRoyaleEquipments.KAMIKAZE,
 BattleRoyaleEquipments.SMOKE,
 BattleRoyaleEquipments.SMOKE_WITH_DAMAGE,
 BattleRoyaleEquipments.ARCADE_SMOKE,
 BattleRoyaleEquipments.FIRE_CIRCLE,
 BattleRoyaleEquipments.CORRODING_SHOT,
 BattleRoyaleEquipments.CLING_BRANDER,
 BattleRoyaleEquipments.ADAPTATION_HEALTH_RESTORE,
 BattleRoyaleEquipments.THUNDER_STRIKE,
 BattleRoyaleEquipments.SHOT_PASSION])

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
BR_COIN = 'brcoin'
