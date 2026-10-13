# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/cgf_blocks.py
from __future__ import absolute_import
import typing
import weakref
from visual_script.block import Meta, Block
from visual_script.misc import ASPECT
from visual_script.contexts.cgf_context import GameObjectWrapper
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.type import VScriptStructField, VScriptStruct
from vehicle_filters import getVehicleFilters

class CGFMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR, ASPECT.SERVER]


class GetEntityGameObject(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(GetEntityGameObject, self).__init__(*args, **kwargs)
        self._entity = self._makeDataInputSlot('entity', SLOT_TYPE.ENTITY)
        self._gameObject = self._makeDataOutputSlot('gameObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def _exec(self):
        entity = self._entity.getValue()
        gameObject = entity.entityGameObject
        goWrapper = GameObjectWrapper(gameObject)
        self._gameObject.setValue(weakref.proxy(goWrapper))


class PrefabsToVehFilter(VScriptStruct):
    filter = VScriptStructField('filter', SLOT_TYPE.STR)
    prefabs = VScriptStructField('prefabs', arrayOf(SLOT_TYPE.STR))

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class GetPrefabsByVehicleFilter(Block, CGFMeta):

    def __init__(self, *args, **kwargs):
        super(GetPrefabsByVehicleFilter, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._filters = self._makeDataInputSlot('filters', arrayOf(PrefabsToVehFilter.slotType()))
        self._defaultPrefabs = self._makeDataInputSlot('default', arrayOf(SLOT_TYPE.STR))
        self._out = self._makeEventOutputSlot('out')
        self._prefabs = self._makeDataOutputSlot('prefabs', arrayOf(SLOT_TYPE.STR), None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]

    def validate(self):
        if not self._vehicle.hasValue():
            return 'Vehicle value is required.'
        if not self._filters.hasValue():
            return 'Filters value is required.'
        return 'Default prefabs value is required.' if not self._defaultPrefabs.hasValue() else super(GetPrefabsByVehicleFilter, self).validate()

    def _execute(self):
        vehicle = self._vehicle.getValue()
        filtersModel = getVehicleFilters()
        prefabs = None
        for prefabsToFilter in self._filters.getValue():
            if filtersModel.isVehicleMatchByFilter(prefabsToFilter.filter, vehicle.typeDescriptor):
                prefabs = prefabsToFilter.prefabs
                break

        if prefabs is None:
            prefabs = self._defaultPrefabs.getValue()
        self._prefabs.setValue(prefabs)
        self._out.call()
        return
