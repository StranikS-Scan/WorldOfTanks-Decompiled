# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptCache.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from visual_script.multi_plan_provider import makeMultiPlanProvider
from visual_script.misc import ASPECT

class VisualScriptCache(DynamicScriptComponent):

    def __init__(self):
        super(VisualScriptCache, self).__init__()
        self._plansBucket = {}

    def onDestroy(self):
        for bucket in self._plansBucket.values():
            for vsePlans in bucket:
                vsePlans.stop()
                vsePlans.destroy()

        self._plansBucket.clear()
        self._plansBucket = None
        return

    def getPlan(self, componentName, planNames):
        if componentName in self._plansBucket:
            for vsePlans in self._plansBucket[componentName]:
                if vsePlans.isLoaded() and all((not vsePlans.get(planName).isActive() for planName in planNames)):
                    return vsePlans

        vsePlans = makeMultiPlanProvider(ASPECT.CLIENT, componentName)
        vsePlans.load(planNames)
        self._plansBucket.setdefault(componentName, []).append(vsePlans)
        return vsePlans
