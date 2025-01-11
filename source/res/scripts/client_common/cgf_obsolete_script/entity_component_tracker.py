# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/cgf_obsolete_script/entity_component_tracker.py
import BigWorld
from cgf_script.entity_dyn_components import BWEntityComponentTracker
from PlayerEvents import g_playerEvents

class BWVehicleComponentTrackerClient(BWEntityComponentTracker):

    def __init__(self):
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    @property
    def _isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def onDynamicComponentCreated(self, component):
        super(BWVehicleComponentTrackerClient, self).onDynamicComponentCreated(component)
        if self._isAvatarReady:
            BigWorld.player().arena.onDynamicComponentCreatedOnVehicle(component)

    def onDynamicComponentDestroyed(self, component):
        super(BWVehicleComponentTrackerClient, self).onDynamicComponentDestroyed(component)
        BigWorld.player().arena.onDynamicComponentDestroyedOnVehicle(component)

    def __onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        for component in self.dynamicComponents.itervalues():
            BigWorld.player().arena.onDynamicComponentCreatedOnVehicle(component)
