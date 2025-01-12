# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptOverrides.py
from copy import copy
import BigWorld

class VisualScriptOverrides(BigWorld.DynamicScriptComponent):

    def updateParams(self, planDefs):
        if not self.params:
            return planDefs
        result = []
        for planDef in planDefs:
            planName = planDef['name']
            planOverrides = self.params.get(planName)
            if planOverrides:
                planDef = copy(planDef)
                oldParams = planDef.get('params', {})
                newParams = copy(oldParams)
                newParams.update(planOverrides)
                planDef['params'] = newParams
            result.append(planDef)

        return result
