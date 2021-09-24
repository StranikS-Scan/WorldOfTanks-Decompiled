# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PublicCounter.py
from helpers import dependency
import ArenaComponents
from script_component.ScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class PublicCounter(DynamicScriptComponent):

    def onAvatarReady(self):
        parent = self.entity.entityGameObject
        parent.createComponent(ArenaComponents.BattleStage, self.counter, self.max)
        self.set_counter(self.counter)

    def set_counter(self, *args):
        guiSessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = guiSessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPublicCounter(self.keyName, self.counter, self.max)
        go = self.entity.entityGameObject
        stageComponent = go.findComponentByType(ArenaComponents.BattleStage)
        if stageComponent is not None:
            go.removeComponentByType(ArenaComponents.BattleStage)
        stageComponent = go.createComponent(ArenaComponents.BattleStage, self.counter, self.max)
        if stageComponent is not None:
            stageComponent.current = self.counter
            stageComponent.maximum = self.max
        return

    def onDestroy(self):
        super(PublicCounter, self).onDestroy()
        parent = self.entity.entityGameObject
        parent.removeComponentByType(ArenaComponents.BattleStage)
