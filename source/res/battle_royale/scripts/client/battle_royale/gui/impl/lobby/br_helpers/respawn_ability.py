# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/br_helpers/respawn_ability.py
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class RespawnAbility(object):
    __brController = dependency.descriptor(IBattleRoyaleController)

    @classmethod
    def getSoloRespawnPeriod(cls):
        return int(cls._getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, 'respawnPeriod'))

    @classmethod
    def getPlatoonRespawnPeriod(cls):
        return int(cls._getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, 'respawnPeriod'))

    @classmethod
    def getPlatoonTimeToResurrect(cls):
        return cls._getParams(ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, 'timeToResurrect')

    @classmethod
    def _getParams(cls, battleType, key):
        config = cls.__brController.getModeSettings().respawns.get(battleType)
        return config[key] if config else None
