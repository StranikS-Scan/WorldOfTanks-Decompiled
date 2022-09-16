# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptCache.py
import BigWorld
from visual_script.misc import ASPECT
from visual_script.multi_plan_provider import MultiPlanCache

class VisualScriptCache(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(VisualScriptCache, self).__init__()
        self._multiPlanCache = MultiPlanCache(ASPECT.CLIENT)

    def onDestroy(self):
        self._multiPlanCache.destroy()

    def getPlan(self, componentName, planNames):
        return self._multiPlanCache.getPlan(componentName, planNames)
