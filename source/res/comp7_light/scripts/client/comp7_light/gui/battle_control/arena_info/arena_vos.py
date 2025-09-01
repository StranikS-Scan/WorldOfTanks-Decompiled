# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_control/arena_info/arena_vos.py
from enum import Enum
from comp7_core.gui.battle_control.arena_info.arena_vos import Comp7CoreKeys
_DEFAULT_ROLE_SKILL_LEVEL = 0

class Comp7LightKeys(Enum):

    @staticmethod
    def getKeys(static=True):
        return [(Comp7CoreKeys.ROLE_SKILL_LEVEL, _DEFAULT_ROLE_SKILL_LEVEL), (Comp7CoreKeys.VOIP_CONNECTED, False)] if static else []

    @staticmethod
    def getSortingKeys(static=True):
        return []
