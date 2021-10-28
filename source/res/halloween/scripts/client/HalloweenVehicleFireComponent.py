# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HalloweenVehicleFireComponent.py
import random
import BigWorld

class HalloweenVehicleFireComponent(BigWorld.DynamicScriptComponent):

    def onEnterWorld(self, *args):
        if self.isOnFire:
            self.__playEffect()

    def onLeaveWorld(self, *args):
        self.__stopEffect()

    def set_isOnFire(self, oldValue):
        if self.isOnFire:
            self.__playEffect()
        else:
            self.__stopEffect()

    def __playEffect(self):
        vehicle = self.entity
        stages, effects, _ = random.choice(vehicle.typeDescriptor.type.effects['flaming'])
        waitForKeyOff = True
        effectListPlayer = vehicle.appearance.boundEffects.addNew(None, effects, stages, waitForKeyOff)
        self._effectsPlayer = effectListPlayer
        return

    def __stopEffect(self):
        if hasattr(self, '_effectsPlayer') and self._effectsPlayer is not None:
            self._effectsPlayer.stop(forceCallback=True)
            del self._effectsPlayer
        return
