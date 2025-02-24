# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/VehicleStunShotComponent.py
import BigWorld
import CGF
from Math import Vector3
from script_component.DynamicScriptComponent import DynamicScriptComponent
from cosmic_prefabs import Debuf

class VehicleStunShotComponent(DynamicScriptComponent):

    def __init__(self):
        super(VehicleStunShotComponent, self).__init__()
        self.__effectGO = None
        return

    def set_timeDebufFinish(self, _):
        target = BigWorld.entities[self.targetID]
        parentGO = target.entityGameObject
        prefabPath = Debuf.STUN_DEBUF
        relativePositionFromParentGO = Vector3(0, 1.5, 0)
        CGF.loadGameObjectIntoHierarchy(prefabPath, parentGO, relativePositionFromParentGO, self.__onEffectGOLoaded)
        curTime = BigWorld.serverTime()
        if curTime <= self.timeDebufFinish:
            delta = self.timeDebufFinish - curTime
            BigWorld.callback(delta, self.__stopEffect)
        else:
            self.__stopEffect()

    def __stopEffect(self):
        if self.__effectGO:
            CGF.removeGameObject(self.__effectGO)
        self.__effectGO = None
        return

    def __onEffectGOLoaded(self, effectGO):
        self.__effectGO = effectGO

    def onDestroy(self):
        self.__stopEffect()
        super(VehicleStunShotComponent, self).onDestroy()
