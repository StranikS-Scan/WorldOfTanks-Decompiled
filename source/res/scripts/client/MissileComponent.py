# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MissileComponent.py
import BigWorld
from Event import Event
from events_core_common.events_core_cgf.missile_system.components import MissileComponent as MissileComponentCGF

class MissileComponent(MissileComponentCGF, BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(MissileComponent, self).__init__()
        self.onAvatarIdReplicated = Event()
        self.onDetonate = Event()

    def set_replicableAvatarId(self, old):
        self.onAvatarIdReplicated(self, self.replicableAvatarId)

    def set_isDetonateProjectile(self, prev):
        self.onDetonate(self)
