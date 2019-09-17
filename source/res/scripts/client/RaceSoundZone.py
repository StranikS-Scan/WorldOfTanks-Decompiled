# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/RaceSoundZone.py
import importlib
import BigWorld
import Svarog
import GenericComponents
import NetworkComponents
from debug_utils import LOG_DEBUG

class RaceSoundZone(BigWorld.Entity):
    ENFORCE_RELOAD = False

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.gameObject = None
        return

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        if not self.prefab:
            return
        self.loadFromScript(self.prefab)

    def loadFromScript(self, script, doReload=False):
        doReload = doReload or RaceSoundZone.ENFORCE_RELOAD
        self.gameObject = Svarog.GameObject(self.spaceID)
        self.gameObject.createComponent(GenericComponents.TransformComponent, self.matrix)
        self.gameObject.createComponent(NetworkComponents.NetworkEntity, self)
        if not script:
            return
        module = importlib.import_module(script)
        if doReload:
            LOG_DEBUG('reloading')
            reload(module)
        module.spaceID = self.spaceID
        module.buildCommon(self.gameObject)
        module.buildClient(self.gameObject)
        self.gameObject.activate()

    def onLeaveWorld(self):
        if self.gameObject is not None:
            self.gameObject.destroy()
        self.gameObject = None
        return

    def reload(self):
        self.loadFromScript(self.prefab, True)
