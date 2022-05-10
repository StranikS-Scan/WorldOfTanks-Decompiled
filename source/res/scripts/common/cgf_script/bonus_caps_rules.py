# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/bonus_caps_rules.py
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.managers_registrator import autoregister
from constants import IS_CLIENT
if IS_CLIENT:
    from Avatar import PlayerAvatar
    from ClientArena import ClientArena

def bonusCapsManager(bonusCap):

    def predicate(spaceID):
        player = BigWorld.player()
        return ARENA_BONUS_TYPE_CAPS.checkAny(player.arenaBonusType, bonusCap) if spaceID != ClientArena.DEFAULT_ARENA_WORLD_ID and isinstance(player, PlayerAvatar) else False

    return autoregister(creationPredicate=predicate)
