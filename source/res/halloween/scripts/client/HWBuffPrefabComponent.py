# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffPrefabComponent.py
from __future__ import absolute_import
import functools
import CGF
import Math
from WeakMethod import WeakMethod
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, Vector3Param

def _onPrefabLoaded(weakCb, objects, queue):
    callback = weakCb()
    return callback(objects, queue) if callback is not None else False


@groupComponent(prefab=StrParam(), offset=Vector3Param(), scale=Vector3Param(default=(1.0, 1.0, 1.0)), rotationYPR=Vector3Param())
class HWBuffPrefabComponent(DynamicScriptComponent):

    def __init__(self):
        super(HWBuffPrefabComponent, self).__init__()
        self.go = None
        return

    def onDestroy(self):
        if self.go:
            self.go.destroy()
            self.go = None
        return

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        if appearance is not None:
            config = self.groupComponentConfig
            transform = Math.createSRTMatrix(config.scale, config.rotationYPR, config.offset)
            CGF.loadAndCreatePrefabWithParent(config.prefab, appearance.gameObject, transform, functools.partial(_onPrefabLoaded, WeakMethod(self._onPrefabLoaded)))
        return

    def _onPrefabLoaded(self, objects, queue):
        root = objects[0]
        self.go = queue.gameObject(root)
        queue.activateGameObject(root)
        return True
