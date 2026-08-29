# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_modifiers_common/__init__.py
from __future__ import absolute_import
import pkgutil
from ExtensionsManager import g_extensionsManager
from battle_modifiers_common.battle_modifiers import BattleParams, ModifiersContext, ConstantsSet, ModifierScope, EXT_DATA_MODIFIERS_KEY, BATTLE_MODIFIERS_TYPE
if 'battle_modifiers' in [ ext.name for ext in g_extensionsManager.activeExtensions ] and pkgutil.find_loader('battle_modifiers_ext'):
    from battle_modifiers_ext.battle_modifiers import BattleModifiers, getDevGlobalModifiers
else:
    from battle_modifiers_common.battle_modifiers import BattleModifiers, getDevGlobalModifiers
__all__ = ('EXT_DATA_MODIFIERS_KEY', 'BATTLE_MODIFIERS_TYPE', 'BattleParams', 'ModifierScope', 'BattleModifiers', 'ModifiersContext', 'getDevGlobalModifiers')
