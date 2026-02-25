# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/__init__.py
from __future__ import absolute_import
from battle_modifiers_ext import battle_params, modification_cache, remappings_cache

def init():
    battle_params.init()
    remappings_cache.init()
    modification_cache.init()
