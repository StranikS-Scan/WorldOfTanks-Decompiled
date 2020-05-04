# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/visual_script_helpers.py
import VSE
from visual_script import ASPECT

def loadAndStartPlayerVSPlans(vsNames):
    vsPlans = []
    if vsNames:
        for vsName in vsNames:
            plan = VSE.Plan()
            plan.load(vsName, [ASPECT.CLIENT])
            plan.start()
            vsPlans.append(plan)

    return vsPlans
