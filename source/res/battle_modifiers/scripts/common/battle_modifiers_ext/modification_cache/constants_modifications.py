# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/modification_cache/constants_modifications.py
from constants import AOI
from battle_modifiers_common.battle_modifiers import BattleParams, ConstantsSet, CONSTANTS_ORIGINAL
from battle_modifiers_ext.constants_ext import USE_CONSTANTS_CACHE, MAX_CONSTANTS_CACHE_LAYER_COUNT, ModifierDomain
from battle_modifiers_ext.modification_cache.modification_cache import ModificationCache
from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING:
    from battle_modifiers_ext.battle_modifiers import BattleModifiers
    from battle_modifiers_common import ModifiersContext
g_cache = None

class ConstantsModification(ConstantsSet):

    def __init__(self, modifiers):
        super(ConstantsModification, self).__init__()
        if modifiers.haveDomain(ModifierDomain.CONSTANTS):
            self.__modifyConstants(modifiers)

    def __modifyConstants(self, modifiers):
        self.VEHICLE_CIRCULAR_AOI_RADIUS = modifiers(BattleParams.VEHICLE_AOI_RADIUS, AOI.VEHICLE_CIRCULAR_AOI_RADIUS)
        self.VEHICLE_CIRCULAR_AOI_RADIUS_HYSTERESIS_MARGIN = self.VEHICLE_CIRCULAR_AOI_RADIUS + AOI.CIRCULAR_AOI_MARGIN


class ConstantsModificationCache(ModificationCache):
    DEFAULT_LAYER_COUNT = MAX_CONSTANTS_CACHE_LAYER_COUNT
    __slots__ = ()

    def get(self, battleModifiers=None):
        if not battleModifiers:
            return CONSTANTS_ORIGINAL
        if not battleModifiers.haveDomain(ModifierDomain.CONSTANTS):
            return CONSTANTS_ORIGINAL
        if not USE_CONSTANTS_CACHE:
            return ConstantsModification(battleModifiers)
        layerId = battleModifiers.id()
        modifications = self._modifications
        if layerId in modifications:
            return modifications[layerId]
        constants = ConstantsModification(battleModifiers)
        self._addLayer(layerId, constants)
        return constants


def init():
    global g_cache
    g_cache = ConstantsModificationCache()
