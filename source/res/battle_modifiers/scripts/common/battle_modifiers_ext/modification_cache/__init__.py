# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/modification_cache/__init__.py
from __future__ import absolute_import
from battle_modifiers_ext.modification_cache import constants_modifications, vehicle_modifications

def init():
    vehicle_modifications.init()
    constants_modifications.init()
