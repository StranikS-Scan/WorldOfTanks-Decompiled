# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/time_bound_prefab_component.py
from datetime import datetime
from functools import partial
import BigWorld
import CGF
import Math
from math_utils import VectorConstant
from cache import cached_property
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery

class _BoundPrefabData(object):
    __slots__ = ('loadCallbackID', 'removeCallbackID', 'prefab', 'iteration')

    def __init__(self):
        super(_BoundPrefabData, self).__init__()
        self.reset()

    def reset(self):
        self.loadCallbackID = -1
        self.removeCallbackID = -1
        self.prefab = None
        self.iteration = 0
        return


@registerComponent
class TimeBoundPrefabComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Time bound prefab loading'
    category = 'Time'
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab path', value='', annotations={'path': '*.prefab'})
    date = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(datetime.now().day, datetime.now().month, datetime.now().year), editorName='Date(DD:MM:YYYY)')
    time = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(datetime.now().hour, datetime.now().minute, 0), editorName='Time(HH:MI:SS)')
    timeToLive = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Time to live(SS)', value=1.0)
    repeatTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Time to Repeat(SS)', value=-1.0)
    repeatCount = ComponentProperty(type=CGFMetaTypes.INT, editorName='Cycles count', value=-1)

    def __init__(self):
        super(TimeBoundPrefabComponent, self).__init__()
        self.prefabData = _BoundPrefabData()

    @cached_property
    def dateTime(self):
        return datetime(int(self.date.z), int(self.date.y), int(self.date.x), int(self.time.x), int(self.time.y), int(self.time.z))


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainEditor)
class _validateProperties(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, TimeBoundPrefabComponent)
    def onAddedDelayedPrefab(self, go, timeBoundComp):
        if timeBoundComp.repeatTime > 0:
            pass


@autoregister(presentInAllWorlds=True)
class TimeBoundPrefabManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, TimeBoundPrefabComponent)
    def onAddedDelayedPrefab(self, go, timeBoundComp):
        self._scheduleCallbacks(go, timeBoundComp)

    @onRemovedQuery(TimeBoundPrefabComponent)
    def onRemovedDelayedPrefab(self, timeBoundComp):
        data = timeBoundComp.prefabData
        if data.removeCallbackID >= 0:
            BigWorld.cancelCallback(data.removeCallbackID)
        if data.loadCallbackID >= 0:
            BigWorld.cancelCallback(data.loadCallbackID)
        if data.prefab is not None:
            CGF.removeGameObject(data.prefab)
        data.reset()
        return

    @classmethod
    def _onGOLoaded(cls, iteration, timeBoundComp, prefab):
        data = timeBoundComp.prefabData
        if iteration != data.iteration:
            CGF.removeGameObject(prefab)
            return
        data.prefab = prefab

    @classmethod
    def _loadGO(cls, go, timeBoundComp):
        data = timeBoundComp.prefabData
        data.loadCallbackID = -1
        callback = partial(cls._onGOLoaded, data.iteration, timeBoundComp)
        CGF.loadGameObjectIntoHierarchy(timeBoundComp.prefabPath, go, VectorConstant.Vector3Zero, callback)

    @classmethod
    def _removeGO(cls, go, timeBoundComp):
        data = timeBoundComp.prefabData
        data.removeCallbackID = -1
        if data.prefab is not None:
            CGF.removeGameObject(data.prefab)
            data.prefab = None
        cls._scheduleCallbacks(go, timeBoundComp)
        return

    @classmethod
    def _scheduleCallbacks(cls, go, timeBoundComp):
        data = timeBoundComp.prefabData
        repeatCount = timeBoundComp.repeatCount
        delay = cls._getDelayTime(timeBoundComp)
        if 0 < repeatCount <= data.iteration or delay < 0.0:
            return
        data.iteration += 1
        loadCallback = partial(cls._loadGO, go, timeBoundComp)
        data.loadCallbackID = BigWorld.callback(delay, loadCallback)
        removeCallback = partial(cls._removeGO, go, timeBoundComp)
        data.removeCallbackID = BigWorld.callback(delay + timeBoundComp.timeToLive, removeCallback)

    @classmethod
    def _now(cls):
        return datetime.now()

    @classmethod
    def _getDelayTime(cls, timeBoundComp):
        now = cls._now()
        expected = timeBoundComp.dateTime
        deltaSeconds = (expected - now).total_seconds()
        repeatTime = timeBoundComp.repeatTime
        if deltaSeconds > 0.0:
            return deltaSeconds
        if repeatTime < 0.0:
            return -1.0
        repeatCount = timeBoundComp.repeatCount
        return -1.0 if repeatCount > 0 and deltaSeconds + (repeatCount - 1) * repeatTime < 0.0 else repeatTime - abs(deltaSeconds) % repeatTime
