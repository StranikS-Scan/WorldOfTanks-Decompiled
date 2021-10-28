# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBossTeleportComponent.py
import BigWorld
import logging
import Math
from effect_controller import EffectController
from helpers import newFakeModel
_logger = logging.getLogger(__name__)

class HWBossTeleportComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        self._teleportModel = None
        self._teleportEffect = EffectController('boss_teleport')
        return

    def playBossTeleport(self, position):
        if not self._teleportModel:
            self._teleportModel = newFakeModel()
            BigWorld.player().addModel(self._teleportModel)
        self._teleportModel.position = position
        self._teleportEffect.playSequence(self._teleportModel)

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        self._teleportEffect.reset()
        self._teleportModel = None
        return
