# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/contexts/cgf_context.py
import weakref
import BigWorld
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script.context import VScriptContext, vse_get_property, vse_event_out
from constants import IS_CELLAPP, IS_UE_EDITOR, IS_CLIENT
from visual_script.dependency import dependencyImporter
if IS_CELLAPP:
    helpers = dependencyImporter('helpers')

class GameObjectWrapper(object):

    def __init__(self, go):
        self.go = go


class CGFGameObjectContext(VScriptContext):

    def __init__(self, gameObject, aspect):
        super(CGFGameObjectContext, self).__init__(aspect)
        self.gameObject = GameObjectWrapper(gameObject)
        if IS_CELLAPP:
            self.__arena = helpers.getArena(gameObject.spaceID)
        else:
            self.__arena = None
        return

    @vse_get_property(SLOT_TYPE.GAME_OBJECT, display_name='Self', description='Returns current context GameObject', aspects=[ASPECT.CLIENT, ASPECT.HANGAR, ASPECT.SERVER])
    def getSelf(self):
        return weakref.proxy(self.gameObject)

    @vse_get_property(SLOT_TYPE.ARENA, display_name='Arena', description='Returns current arena', aspects=[ASPECT.SERVER])
    def getArena(self):
        return weakref.proxy(self.__arena)

    @vse_event_out((), display_name='OnClick', description='Reacts on click on game object                      (only if go have CollisionComponent, IsSelectableComponent, VSEComponent)', aspects=[ASPECT.CLIENT, ASPECT.HANGAR])
    def onGameObjectClick(self):
        pass

    @vse_event_out((), display_name='OnHoverIn', description='Reacts on hover over game object                      (only if go have CollisionComponent, VSEComponent)', aspects=[ASPECT.CLIENT, ASPECT.HANGAR])
    def onGameObjectHoverIn(self):
        pass

    @vse_event_out((), display_name='OnHoverOut', description='Reacts on exit from hover over game object                      (only if go have CollisionComponent, VSEComponent)', aspects=[ASPECT.CLIENT, ASPECT.HANGAR])
    def onGameObjectHoverOut(self):
        pass

    @vse_event_out(SLOT_TYPE.STR, display_name='OnTrigger', description='Custom triggered event', aspects=[ASPECT.CLIENT, ASPECT.HANGAR])
    def onTriggerEvent(self, eventName):
        pass


def getCurrentAspect():
    if IS_CELLAPP:
        return ASPECT.SERVER
    if IS_CLIENT:
        from Account import PlayerAccount
        if isinstance(BigWorld.player(), PlayerAccount):
            return ASPECT.HANGAR
        return ASPECT.CLIENT
    return ASPECT.CLIENT


def createContext(go):
    aspect = getCurrentAspect()
    return CGFGameObjectContext(go, aspect)


def getPlanTags():
    from visual_script.plan_tags import PlanTags
    return PlanTags().tags
