# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/contexts/entity_context.py
import weakref
from visual_script.context import VScriptContext, vse_get_property
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE

class EntityContextClient(VScriptContext):

    def __init__(self, owner):
        super(EntityContextClient, self).__init__(ASPECT.CLIENT)
        self._owner = owner

    def destroy(self):
        super(EntityContextClient, self).destroy()
        self._owner = None
        return

    @vse_get_property(SLOT_TYPE.ENTITY, display_name='Self', description='Return instance of current entity', aspects=[ASPECT.CLIENT])
    def getSelf(self):
        return weakref.proxy(self._owner.entity)
