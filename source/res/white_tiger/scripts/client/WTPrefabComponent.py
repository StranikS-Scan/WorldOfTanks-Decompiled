# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTPrefabComponent.py
from white_tiger.helpers.prefab_helpers import PrefabHandlerComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent

class WTPrefabComponent(PrefabHandlerComponent, DynamicScriptComponent):

    def _onAvatarReady(self):
        self.createGameObject()

    def onAppearanceReady(self):
        self.setAppearanceReady()

    def createGameObject(self):
        parent = self.entity.entityGameObject
        if parent is not None:
            self.loadGameObject(self.entity, self.prefab, parent, self.matrix)
        return

    def onDestroy(self):
        self.destroyGameObject()
        super(WTPrefabComponent, self).onDestroy()
