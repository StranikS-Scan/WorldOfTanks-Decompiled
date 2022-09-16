# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/__init__.py
import battle_params
import battle_modifiers
import vehicle_modifications

def init():
    battle_params.init()
    battle_modifiers.init()
    vehicle_modifications.init()


def getGlobalModifiers():
    return battle_modifiers.g_cache


def getModificationCache():
    return vehicle_modifications.g_cache
