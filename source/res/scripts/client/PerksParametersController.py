# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PerksParametersController.py
import typing
from collections import defaultdict
from WeakMethod import WeakMethodProxy
from BasePerksController import BasePerksController
from PerkPlanHolder import RestartingMultiPlan

class RecalcType:
    INITIAL = 1
    COMPARING = 2
    DEFAULT = 3


class PlanOwner(object):

    def __init__(self, _id):
        self.id = _id


class PerksParametersController(BasePerksController):

    def __init__(self, ownerIntCD, scopedPerks):
        owner = PlanOwner(ownerIntCD)
        super(PerksParametersController, self).__init__(owner, scopedPerks)
        self.__destroyed = False
        self._vehParams = None
        self._initialized = False
        self._isRunning = False
        self._ownerIntCD = ownerIntCD
        self._recalcType = RecalcType.INITIAL
        self._ignoredPerks = []
        return

    def __del__(self):
        if not self.__destroyed:
            self.destroy()

    def destroy(self):
        super(PerksParametersController, self).destroy()
        self._vehParams = None
        self.__destroyed = True
        return

    def recalc(self, vehParams=None):
        if vehParams:
            self.setVehParams(vehParams)
            self._recalcType = RecalcType.INITIAL
        else:
            self._recalcType = RecalcType.DEFAULT
        if not self._initialized:
            self.init(True)
            self._initialized = True
        else:
            self.recalcFactors()
        if not self._scopedPerks or self._planHolder.allPerksDone():
            self.rebuildParams()

    def setVehParams(self, vehParams):
        self._vehParams = vehParams

    def restore(self):
        self._planHolder.restorePlans(self._ignoredPerks)
        del self._ignoredPerks[:]

    def customizedRecalc(self, perkName):
        self._ignoredPerks.append(perkName)
        self._recalcType = RecalcType.COMPARING
        self._planHolder.deactivatePerk(perkName)

    def init(self, isAutoStart=False):
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        self._planHolder = RestartingMultiPlan(self._scopedPerks, WeakMethodProxy(self.rebuildParams))
        self._planHolder.loadPlan(self._owner, isAutoStart)
        self._isRunning = True

    def reload(self, scopedPerks):
        self._recalcType = RecalcType.INITIAL
        self.resetFactors()
        if self._planHolder:
            self._planHolder.reload(self._owner, scopedPerks)
            if not self._scopedPerks or self._planHolder.allPerksDone():
                self.rebuildParams()

    def recalcFactors(self):
        self.resetFactors()
        self._isRunning = True
        self._planHolder.reloadPlans()

    def resetFactors(self):
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))

    def isEnabled(self):
        return self._isRunning

    def isInitialized(self):
        return self._initialized

    def rebuildParams(self):
        self._isRunning = False
        if self._recalcType == RecalcType.INITIAL and self._vehParams:
            self._vehParams.rebuildParams()
