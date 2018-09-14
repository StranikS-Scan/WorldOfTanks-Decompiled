# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OcclusionDecal.py
import BigWorld
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartNames

class OcclusionDecal:
    settingsCore = dependency.descriptor(ISettingsCore)

    @staticmethod
    def isEnabled():
        return BigWorld.isForwardPipeline() is False and BigWorld.isSSAOEnabled() and BigWorld.isShadowsEnabled()

    def __init__(self):
        self.__attached = False
        self.__typeDesc = None
        self.__model = None
        self.__chassisDecals = []
        self.__chassisParent = None
        self.__hullDecals = []
        self.__hullParent = None
        self.__turretDecals = []
        self.__turretParent = None
        self.settingsCore.onSettingsChanged += self.onSettingsChanged
        return

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.onSettingsChanged
        self.__typeDesc = None
        self.detach()
        return

    def attach(self, typeDesc, model, isSettingChanged=False):
        self.__typeDesc = typeDesc
        self.__model = model
        if not isSettingChanged:
            if not OcclusionDecal.isEnabled() or self.__attached:
                return
        elif self.__attached:
            return
        self.__attached = True
        self.__chassisParent = model.root
        for transform in typeDesc.chassis['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__chassisParent, False)
            self.__chassisDecals.append(decal)

        self.__hullParent = model.node(TankPartNames.HULL)
        for transform in typeDesc.hull['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__hullParent, True)
            self.__hullDecals.append(decal)

        self.__turretParent = model.node(TankPartNames.TURRET)
        for transform in typeDesc.turret['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__turretParent, True)
            self.__turretDecals.append(decal)

    def detach(self):
        if not self.__attached:
            return
        else:
            self.__attached = False
            for decal in self.__chassisDecals:
                self.__chassisParent.detach(decal)

            self.__chassisDecals = []
            self.__chassisParent = None
            for decal in self.__hullDecals:
                self.__hullParent.detach(decal)

            self.__hullDecals = []
            self.__hullParent = None
            for decal in self.__turretDecals:
                self.__turretParent.detach(decal)

            self.__turretDecals = []
            self.__turretParent = None
            self.__model = None
            return

    def __reattach(self):
        if self.__attached:
            return
        elif self.__typeDesc is None or self.__model is None:
            return
        else:
            self.attach(self.__typeDesc, self.__model, True)
            return

    def onSettingsChanged(self, diff=None):
        enabled = False
        if 'SHADOWS_QUALITY' in diff:
            value = diff['SHADOWS_QUALITY']
            if value < 4 and OcclusionDecal.isEnabled():
                enabled = True
            if enabled:
                self.__reattach()
            else:
                self.detach()

    @staticmethod
    def __createDecal(transform, parentNode, applyToAll):
        diffuseTexture = ''
        bumpTexture = ''
        hmTexture = ''
        addTexture = 'maps/spots/TankOcclusion/TankOcclusionMap.dds'
        priority = 0
        materialType = 4
        visibilityMask = 4294967295L
        accuracy = 2
        influence = 30
        if applyToAll:
            influence = 62
        decal = BigWorld.WGOcclusionDecal()
        decal.create(diffuseTexture, bumpTexture, hmTexture, addTexture, priority, materialType, influence, visibilityMask, accuracy)
        decal.setLocalTransform(transform)
        parentNode.attach(decal)
        return decal
