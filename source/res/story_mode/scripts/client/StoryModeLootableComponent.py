# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/StoryModeLootableComponent.py
import CGF
import Math
from GenericComponents import TransformComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from Event import SafeEvent, EventManager

class StoryModeLootableComponent(DynamicScriptComponent):
    _PREFAB_URL_BY_STYLE = {'SM_LOOT_EQUIPMENT': 'content/CGFPrefabs/Storymode/loot.prefab',
     'SM_LOOT_PLAN': 'content/CGFPrefabs/Storymode/loot.prefab',
     'SM_LOOT_TANK': 'content/CGFPrefabs/Storymode/loot_yellow.prefab'}

    def __init__(self, *args, **kwargs):
        super(StoryModeLootableComponent, self).__init__(*args, **kwargs)
        self._prefab = None
        self._eventManager = EventManager()
        self.onStartCapturing = SafeEvent(self._eventManager)
        self.onStopCapturing = SafeEvent(self._eventManager)
        self._loadPrefab()
        return

    def set_startTime(self, prevValue):
        if self.startTime == -1:
            self.onStopCapturing()
            return
        self.onStartCapturing(self.startTime, self.captureTime)

    def onDestroy(self):
        self._eventManager.clear()
        super(StoryModeLootableComponent, self).onDestroy()

    def _loadPrefab(self):
        if self.markerStyle in self._PREFAB_URL_BY_STYLE:
            CGF.loadGameObjectIntoHierarchy(self._PREFAB_URL_BY_STYLE[self.markerStyle], self.entity.entityGameObject, Math.Vector3(), self._onPrefabLoaded)

    def _onPrefabLoaded(self, prefab):
        self._prefab = prefab
        self._prefab.activate()
        transform = self._prefab.findComponentByType(TransformComponent)
        if transform:
            transform.scale = Math.Vector3(self.radius, 1.0, self.radius)
