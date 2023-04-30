# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/perk_context_impl_base.py
from visual_script.misc import ASPECT

class PerkContextImplBase(object):

    def __init__(self, perksControllerWeakRef, perkID, perkLevel, scopeID):
        self._perksController = perksControllerWeakRef
        self._perkLevel = perkLevel
        self.perkID = perkID
        self.scopeID = scopeID
        self.vehicleID = perksControllerWeakRef.vehicleID

    @property
    def vehicle(self):
        raise NotImplementedError

    @property
    def perkLevel(self):
        raise NotImplementedError

    @perkLevel.setter
    def perkLevel(self, value):
        raise NotImplementedError

    def addFactorModifier(self, factor, value):
        raise NotImplementedError

    def removeFactorModifiers(self, factor, numMods):
        raise NotImplementedError

    def dropAllPerkModifiers(self):
        raise NotImplementedError

    def notifyOnClient(self, *_):
        raise NotImplementedError

    def notifyOnClientRibbon(self, *_):
        raise NotImplementedError


class CrewContextImplBase(PerkContextImplBase):
    ASPECT = ASPECT.ALL

    def __init__(self, perksControllerWeakRef, perkID, perkLevel, scopeID, tmanIdxs):
        super(PerkContextImplBase).__init__(perksControllerWeakRef, perkID, perkLevel, scopeID)
        self._levelOverride = False
        self._tmanIdxs = tmanIdxs
