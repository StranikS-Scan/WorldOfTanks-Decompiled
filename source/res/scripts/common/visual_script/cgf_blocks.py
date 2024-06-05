# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/cgf_blocks.py
import weakref
from visual_script.block import Meta, Block
from visual_script.misc import ASPECT
from visual_script.contexts.cgf_context import GameObjectWrapper
from visual_script.slot_types import SLOT_TYPE

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
