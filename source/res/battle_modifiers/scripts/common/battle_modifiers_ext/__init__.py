# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/__init__.py
import battle_params
import remappings_cache
import vehicle_modifications

def init():
    battle_params.init()
    remappings_cache.init()
    vehicle_modifications.init()


def getModificationCache():
    return vehicle_modifications.g_cache
