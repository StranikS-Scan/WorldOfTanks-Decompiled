# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PublicCounter.py
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class PublicCounter(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.set_counter(self.counter)

    def set_counter(self, *args):
        ctrl = self.entity.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPublicCounter(self.counter, self.max)
        go = self.entity.entityGameObject
        go.removeComponentByType(GenericComponents.BattleStage)
        go.createComponent(GenericComponents.BattleStage, self.counter, self.max)
        return

    def onDestroy(self):
        super(PublicCounter, self).onDestroy()
        parent = self.entity.entityGameObject
        parent.removeComponentByType(GenericComponents.BattleStage)