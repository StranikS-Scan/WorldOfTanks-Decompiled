# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicleDecal.py
import weakref
import BigWorld
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartNames

class VehicleDecal(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    DECALS_OFF = 0
    OCCLUSION_DECAL = 1

    @staticmethod
    def getDecalType():
        decalType = VehicleDecal.DECALS_OFF
        if not BigWorld.isForwardPipeline():
            if BigWorld.isShadowsEnabled() and BigWorld.isSSAOEnabled():
                decalType = VehicleDecal.OCCLUSION_DECAL
        return decalType

    def __init__(self, appearance):
        self.__attached = False
        self.__appearance = weakref.proxy(appearance)
        self.__chassisDecals = []
        self.__chassisParent = None
        self.__hullDecals = []
        self.__hullParent = None
        self.__turretDecals = []
        self.__turretParent = None
        return

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.onSettingsChanged
        self.detach()
        self.__chassisDecals = None
        self.__hullDecals = None
        self.__turretDecals = None
        self.__appearance = None
        return

    def create(self):
        self.__createDecals(VehicleDecal.getDecalType())
        self.settingsCore.onSettingsChanged += self.onSettingsChanged

    def attach(self):
        if self.__attached or self.__appearance is None:
            return
        else:
            self.__attach()
            return

    def detach(self):
        if not self.__attached:
            return
        else:
            self.__attached = False
            for decal in self.__chassisDecals:
                self.__chassisParent.detach(decal)

            self.__chassisParent = None
            for decal in self.__hullDecals:
                self.__hullParent.detach(decal)

            self.__hullParent = None
            for decal in self.__turretDecals:
                self.__turretParent.detach(decal)

            self.__turretParent = None
            return

    def __reattach(self, decalType):
        self.detach()
        self.__createDecals(decalType)
        self.__attach()

    def onSettingsChanged(self, diff=None):
        if 'SHADOWS_QUALITY' in diff:
            decalType = VehicleDecal.getDecalType()
            enabled = decalType == VehicleDecal.OCCLUSION_DECAL
            if enabled:
                self.__reattach(decalType)
            else:
                self.detach()

    def __createDecals(self, decalType):
        if self.__appearance is None:
            return
        else:
            typeDesc = self.__appearance.typeDescriptor
            if typeDesc is None:
                return
            self.__chassisDecals = []
            self.__hullDecals = []
            self.__turretDecals = []
            if decalType != VehicleDecal.OCCLUSION_DECAL:
                return
            for transform in typeDesc.chassis.AODecals:
                decal = self.__createDecal(transform, False)
                self.__chassisDecals.append(decal)

            for transform in typeDesc.hull.AODecals:
                decal = self.__createDecal(transform, True)
                self.__hullDecals.append(decal)

            for transform in typeDesc.turret.AODecals:
                decal = self.__createDecal(transform, True)
                self.__turretDecals.append(decal)

            return

    def __attach(self):
        model = self.__appearance.compoundModel
        if model is None:
            return
        else:
            self.__chassisParent = model.root
            self.__hullParent = model.node(TankPartNames.HULL)
            self.__turretParent = model.node(TankPartNames.TURRET)
            for decal in self.__chassisDecals:
                self.__chassisParent.attach(decal)

            for decal in self.__hullDecals:
                self.__hullParent.attach(decal)

            for decal in self.__turretDecals:
                self.__turretParent.attach(decal)

            self.__attached = True
            return

    def __createDecal(self, transform, applyToAll):
        addTexture = 'maps/spots/TankOcclusion/TankOcclusionMap.dds'
        priority = 0
        influence = 30
        if applyToAll:
            influence = 62
        diffuseTexture = ''
        bumpTexture = ''
        hmTexture = ''
        materialType = 4
        visibilityMask = 4294967295L
        accuracy = 2
        decal = BigWorld.WGOcclusionDecal()
        decal.create(diffuseTexture, bumpTexture, hmTexture, addTexture, priority, materialType, influence, visibilityMask, accuracy)
        decal.setLocalTransform(transform)
        return decal
