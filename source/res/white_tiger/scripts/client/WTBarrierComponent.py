# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTBarrierComponent.py
import BigWorld
from Event import Event
from white_tiger_common.common_cgf.barrier.components import WTBarrierComponent as WTBarrierComponentCGF

class WTBarrierComponent(WTBarrierComponentCGF, BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(WTBarrierComponent, self).__init__()
        self.onReplicationDone = Event()
        self.onChangeMode = Event()

    def onDestroy(self):
        self.onReplicationDone.clear()
        BigWorld.DynamicScriptComponent.onDestroy(self)

    def set_replicableAvatarId(self, old):
        self.onReplicationDone(self)

    def set_mode(self, old):
        self.onChangeMode(self, self.mode)
