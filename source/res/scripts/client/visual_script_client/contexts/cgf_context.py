# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/contexts/cgf_context.py
import weakref
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script.context import VScriptContext, vse_get_property

class GameObjectWrapper(object):

    def __init__(self, go):
        self.go = go


class CGFGameObjectContext(VScriptContext):

    def __init__(self, gameObject):
        super(CGFGameObjectContext, self).__init__(ASPECT.CLIENT)
        self.gameObject = GameObjectWrapper(gameObject)

    @vse_get_property(SLOT_TYPE.GAME_OBJECT, display_name='Self', description='Returns current context GameObject', aspects=[ASPECT.CLIENT])
    def getSelf(self):
        return weakref.proxy(self.gameObject)


def createContext(go):
    return CGFGameObjectContext(go)
