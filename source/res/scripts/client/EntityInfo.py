# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityInfo.py
from script_component.ScriptComponent import DynamicScriptComponent
from cgf_script.component_meta_class import CGFComponent

class CampComponent(CGFComponent):

    def __init__(self, campIndex):
        super(CampComponent, self).__init__()
        self.campIndex = campIndex


class EntityInfo(DynamicScriptComponent):

    def onAvatarReady(self):
        self.set_absoluteIndex()

    def set_absoluteIndex(self, *_):
        if self.label == 'camp':
            gameObject = self.entity.entityGameObject
            if gameObject.findComponentByType(CampComponent) is None:
                gameObject.createComponent(CampComponent, self.absoluteIndex)
        return
