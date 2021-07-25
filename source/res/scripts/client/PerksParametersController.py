# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PerksParametersController.py
from collections import defaultdict
import weakref
import typing
from BasePerksController import BasePerksController
from PerkPlanHolder import RestartingMultiPlan
from items.components.detachment_components import mergePerks
from items.AbilitiesManager import AbilitiesManager
from visual_script.contexts.perks_context import PerkContext
from PerkContextClientImpl import PerkContextClientImpl
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters

class RecalcType:
    INITIAL = 1
    COMPARING = 2
    DEFAULT = 3


class PlanOwner(object):

    def __init__(self, _id):
        self.id = _id


class PerksParametersController(BasePerksController):

    def __init__(self, ownerIntCD, detInvID, scopedPerks):
        owner = PlanOwner(ownerIntCD)
        super(PerksParametersController, self).__init__(owner, scopedPerks)
        self.__destroyed = False
        self._vehParams = None
        self._initialized = False
        self._isRunning = False
        self._ownerIntCD = ownerIntCD
        self._detInvID = detInvID
        self._recalcType = RecalcType.INITIAL
        self.__onStartCallback = None
        self.__ignoredAbilities = None
        self.__crewMasteryIgnored = False
        return

    def __del__(self):
        if not self.__destroyed:
            self.destroy()

    def destroy(self):
        super(PerksParametersController, self).destroy()
        self.__onStartCallback = None
        self._vehParams = None
        self.__destroyed = True
        return

    def recalc(self, initial=False):
        self._recalcType = RecalcType.INITIAL if initial else RecalcType.DEFAULT
        if not self._initialized:
            self.init(True)
            self._initialized = True
        else:
            self.recalcFactors()
        rebuilded = False
        if self.isStarted():
            rebuilded = self._rebuildParams()
        return rebuilded

    def setOnStartCallback(self, callback):
        if callback and self.isStarted():
            callback()
        else:
            self.__onStartCallback = callback

    def ignoreCrewMastery(self):
        self.__crewMasteryIgnored = True

    def getCrewMasteryIgnored(self):
        return self.__crewMasteryIgnored

    @property
    def detInvID(self):
        return self._detInvID

    @property
    def scopedPerks(self):
        return self._scopedPerks

    @property
    def mergedPerks(self):
        return mergePerks(*[ dict(scope) for scope in self._scopedPerks.values() ])

    def setVehParams(self, vehParams):
        self._vehParams = vehParams

    def restore(self, reloadPlans=True):
        if reloadPlans and self.__ignoredAbilities:
            scopedPerksList = self.__ignoredAbilities.getPerksListByVehicle(self.vehicleID)
            self._planHolder.restorePlans(scopedPerksList)
            self.__ignoredAbilities.removePerksByVehicle(self.vehicleID)
        self.__crewMasteryIgnored = False

    def deactivatePerk(self, scopeID, perkID):
        if scopeID not in self.scopedPerks:
            return
        for pID, pLevel in self.scopedPerks[scopeID]:
            if perkID == pID:
                self.customizedRecalc(scopeID, {perkID: pLevel})
                return

    def customizedRecalc(self, scope, perks):
        self._recalcType = RecalcType.COMPARING
        self._planHolder.recalcPerks(scope, perks)
        if not self.__ignoredAbilities:
            self.__ignoredAbilities = AbilitiesManager()
        self.__ignoredAbilities.modifyBuild(self.vehicleID, scope, perks)

    def modifyFactor(self, factor, scopeID, perkID, value):
        self.dropFactorModifiers(factor, scopeID, perkID)
        super(PerksParametersController, self).modifyFactor(factor, scopeID, perkID, value)

    def init(self, isAutoStart=False, contextCreator=None):
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        controllerWeakRef = weakref.proxy(self)
        self._schedulePlans()

        def _contextCreator(*args):
            return PerkContext(PerkContextClientImpl, controllerWeakRef, *args)

        contextCreator = contextCreator or _contextCreator
        self._planHolder = RestartingMultiPlan(self._scopedPerks)
        self._planHolder.loadPlan(contextCreator, self._owner, isAutoStart)
        self._isRunning = True

    def reload(self, scopedPerks):
        self._recalcType = RecalcType.INITIAL
        self.resetFactors()
        if self._planHolder:
            self._planHolder.reload(self._owner, scopedPerks)
            if self.isStarted():
                self._rebuildParams()

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

    def isStarted(self):
        return not self._scopedPerks or self._allPerksLoaded()

    def _rebuildParams(self):
        rebuilded = False
        if self._recalcType == RecalcType.INITIAL and self._vehParams:
            self._vehParams.rebuildParams()
            rebuilded = True
        if self._recalcType != RecalcType.COMPARING and self.__onStartCallback:
            self.__onStartCallback()
            self.__onStartCallback = None
        self._isRunning = False
        return rebuilded

    def getPerkIgnoredLevel(self, scopeID, perkID):
        return 0 if not self.__ignoredAbilities else self.__ignoredAbilities.getPerkLevelByVehicle(self.vehicleID, scopeID, perkID)

    def startPerkNotify(self, scopeId, perkId):
        super(PerksParametersController, self).startPerkNotify(scopeId, perkId)
        if self._allPerksLoaded() and not self._planHolder.inProcess:
            self._rebuildParams()
