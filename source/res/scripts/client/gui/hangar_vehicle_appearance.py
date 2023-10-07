# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_vehicle_appearance.py
import logging
import weakref
import math
from collections import namedtuple
from typing import TYPE_CHECKING
from functools import partial
import BigWorld
import Event
import Math
import VehicleStickers
import Vehicular
import math_utils
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from items.components.c11n_constants import EASING_TRANSITION_DURATION
from gui import g_tankActiveCamouflage
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.simple_turret_rotator import SimpleTurretRotator
from skeletons.gui.customization import ICustomizationService
from vehicle_outfit.outfit import Area, ANCHOR_TYPE_TO_SLOT_TYPE_MAP, SLOT_TYPES
from gui.shared.gui_items.customization.slots import SLOT_ASPECT_RATIO, BaseCustomizationSlot, EmblemSlot, getProgectionDecalAspect
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from items.components.c11n_constants import ApplyArea
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.turret_gun_angles import ITurretAndGunAngles
from vehicle_systems import camouflages
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from vehicle_systems.tankStructure import ModelsSetParams, TankPartNames, ColliderTypes, TankPartIndexes
from vehicle_systems.tankStructure import VehiclePartsTuple, TankNodeNames
from cgf_obsolete_script.script_game_object import ComponentDescriptor, ScriptGameObject
from vehicle_systems.stricted_loading import makeCallbackWeak
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.ClientHangarSpace import hangarCFG
from gui.battle_control.vehicle_getter import hasTurretRotator
from cgf_components.hangar_camera_manager import HangarCameraManager
import GenericComponents
import CGF
if TYPE_CHECKING:
    from vehicle_outfit.outfit import Outfit as TOutfit
    from items.vehicles import VehicleDescrType
_SHOULD_CHECK_DECAL_UNDER_GUN = True
_PROJECTION_DECAL_OVERLAPPING_FACTOR = 0.7
_HANGAR_TURRET_SHIFT = math.pi / 8
_CAMERA_CAPSULE_GUN_SCALE = Math.Vector3(1.0, 1.0, 1.1)
_CAMERA_CAPSULE_SCALE = Math.Vector3(1.5, 1.5, 1.5)
_CAMERA_MIN_DIST_FACTOR = 0.8
AnchorLocation = namedtuple('AnchorLocation', ['position', 'normal', 'up'])
AnchorId = namedtuple('AnchorId', ('slotType', 'areaId', 'regionIdx'))
AnchorHelper = namedtuple('AnchorHelper', ['location',
 'descriptor',
 'turretYaw',
 'partIdx',
 'attachedPartIdx'])
AnchorParams = namedtuple('AnchorParams', ['location', 'descriptor', 'id'])
_logger = logging.getLogger(__name__)

class _LoadStateNotifier(object):
    __em = Event.EventManager()

    def __init__(self, loaded=False):
        self._onLoaded = Event.Event(self.__em)
        self._onUnloaded = Event.Event(self.__em)
        self.__loaded = loaded

    def destroy(self):
        self.__em.clear()

    @property
    def isLoaded(self):
        return self.__loaded

    def subscribe(self, onLoadCallback, onUnloadCallback):
        self._onLoaded += onLoadCallback
        self._onUnloaded += onUnloadCallback

    def unsubscribe(self, onLoadCallback, onUnloadCallback):
        self._onLoaded -= onLoadCallback
        self._onUnloaded -= onUnloadCallback

    def load(self):
        self.__loaded = True
        BigWorld.callback(0.0, makeCallbackWeak(self._onLoaded))

    def unload(self):
        self.__loaded = False
        self._onUnloaded()


class HangarVehicleAppearance(ScriptGameObject):
    __ROOT_NODE_NAME = 'V'
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    settingsCore = dependency.descriptor(ISettingsCore)
    turretAndGunAngles = dependency.descriptor(ITurretAndGunAngles)
    customizationService = dependency.descriptor(ICustomizationService)
    wheelsAnimator = ComponentDescriptor()
    trackNodesAnimator = ComponentDescriptor()
    collisions = ComponentDescriptor()
    shadowManager = ComponentDescriptor()
    dirtComponent = ComponentDescriptor()
    c11nComponent = ComponentDescriptor()
    tracks = ComponentDescriptor()
    collisionObstaclesCollector = ComponentDescriptor()
    tessellationCollisionSensor = ComponentDescriptor()
    flagComponent = ComponentDescriptor()

    @property
    def compoundModel(self):
        return self.__vEntity.model if self.__vEntity else None

    @property
    def id(self):
        return self.__vEntity.id

    fashion = property(lambda self: self.__fashions[0])
    fashions = property(lambda self: self.__fashions)

    @property
    def filter(self):
        return None

    isVehicleDestroyed = property(lambda self: self.__isVehicleDestroyed)

    def __init__(self, spaceId, vEntity):
        ScriptGameObject.__init__(self, vEntity.spaceID, 'HangarVehicleAppearance')
        self.__loadState = _LoadStateNotifier()
        self.__curBuildInd = 0
        self.__vDesc = None
        self.__vState = None
        size = len(TankPartNames.ALL)
        self.__fashions = VehiclePartsTuple(*([None] * size))
        self.__repaintHandlers = [None] * size
        self.__camoHandlers = [None] * size
        self.__projectionDecalsHandlers = [None] * size
        self.__projectionDecalsUpdater = None
        self.__spaceId = spaceId
        self.__vEntity = weakref.proxy(vEntity)
        self.__onLoadedCallback = None
        self.__onLoadedAfterRefreshCallback = None
        self.__vehicleStickers = None
        self.__isVehicleDestroyed = False
        self.__outfit = None
        self.__staticTurretYaw = 0.0
        self.__staticGunPitch = 0.0
        self.__anchorsHelpers = None
        self.__anchorsParams = None
        self.__attachments = []
        self.__modelAnimators = []
        self._modelCollisions = None
        self._crashedModelCollisions = None
        self.shadowManager = None
        self.turretRotator = None
        cfg = hangarCFG()
        self.__currentEmblemsAlpha = cfg['emblems_alpha_undamaged']
        self.__showMarksOnGun = self.settingsCore.getSetting('showMarksOnGun')
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.itemsCache.onSyncCompleted += self.__onItemsCacheSyncCompleted
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.undamagedStateChildren = []
        return

    def recreate(self, vDesc, vState=None, callback=None, outfit=None):
        self.__onLoadedCallback = callback
        self.__reload(vDesc, vState or self.__vState, outfit or self._getActiveOutfit(vDesc))

    def remove(self):
        self.__clearModelAnimators()
        self.__loadState.unload()
        if self.shadowManager is not None:
            self.shadowManager.updatePlayerTarget(None)
            if self.__vEntity.model is not None:
                self.shadowManager.unregisterCompoundModel(self.__vEntity.model)
        self.__vDesc = None
        self.__vState = None
        self.__isVehicleDestroyed = False
        self.__vEntity.model = None
        self.reset()
        if self.collisions:
            BigWorld.removeCameraCollider(self.collisions.getColliderID())
            self.collisions = None
        return

    def refresh(self, outfit=None, callback=None):
        if self.__loadState.isLoaded and self.__vDesc:
            if callback is not None:
                self.__onLoadedAfterRefreshCallback = callback
            self.__reload(self.__vDesc, self.__vState, outfit or self.__outfit)
        return

    def destroy(self):
        if self.fashion is not None:
            self.fashion.removePhysicalTracks()
        if self.shadowManager is not None:
            self.shadowManager.updatePlayerTarget(None)
        if self.tracks is not None:
            self.tracks.reset()
        if self.shadowManager is not None and self.__vEntity.model is not None:
            self.shadowManager.unregisterCompoundModel(self.__vEntity.model)
        self.__clearModelAnimators()
        self.__vehicleStickers = None
        ScriptGameObject.deactivate(self)
        ScriptGameObject.destroy(self)
        self.__vDesc = None
        self.__vState = None
        self.__loadState.unload()
        self.__loadState.destroy()
        self.__loadState = None
        self.__curBuildInd = 0
        self.__vEntity = None
        self.__onLoadedCallback = None
        self.__onLoadedAfterRefreshCallback = None
        self.turretRotator = None
        self.undamagedStateChildren = []
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.itemsCache.onSyncCompleted -= self.__onItemsCacheSyncCompleted
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        return

    @property
    def loadState(self):
        return self.__loadState

    @property
    def fakeShadowDefinedInHullTexture(self):
        return self.__vDesc.hull.hangarShadowTexture if self.__vDesc else None

    def isLoaded(self):
        return self.__loadState.isLoaded

    def recreateRequired(self, newOutfit):
        shouldUpdateModelsSet = self.__outfit.modelsSet != newOutfit.modelsSet
        shouldUpdateAttachments = not self.__outfit.attachments.isEqual(newOutfit.attachments)
        shouldUpdateProgressiveOutfit = False
        if newOutfit.style and newOutfit.style.isProgression:
            if self.__outfit.style and self.__outfit.style.isProgression is False:
                shouldUpdateProgressiveOutfit = True
            elif newOutfit.progressionLevel != self.__outfit.progressionLevel:
                shouldUpdateProgressiveOutfit = True
        return shouldUpdateModelsSet or shouldUpdateAttachments or shouldUpdateProgressiveOutfit

    def computeVehicleHeight(self):
        gunLength = 0.0
        height = 0.0
        if self.collisions is not None:
            desc = self.__vDesc
            hullBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
            turretBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.TURRET))
            gunBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN))
            hullTopY = desc.chassis.hullPosition[1] + hullBB[1][1]
            turretTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + turretBB[1][1]
            gunTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + desc.turret.gunPosition[1] + gunBB[1][1]
            gunLength = math.fabs(gunBB[1][2] - gunBB[0][2])
            height = max(hullTopY, max(turretTopY, gunTopY))
        return (height, gunLength)

    def computeVehicleLength(self):
        vehicleLength = 0.0
        if self.collisions is not None:
            hullBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
            vehicleLength = abs(hullBB[1][2] - hullBB[0][2])
        return vehicleLength

    def computeFullVehicleLength(self):
        hullBB = Math.Matrix(self.__vEntity.model.getBoundsForPart(TankPartIndexes.HULL))
        return hullBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length

    def _getTurretYaw(self):
        return self.turretAndGunAngles.getTurretYaw()

    def _getGunPitch(self):
        return self.turretAndGunAngles.getGunPitch()

    def __reload(self, vDesc, vState, outfit):
        self.__clearModelAnimators()
        self.__loadState.unload()
        if self.fashion is not None:
            self.fashion.removePhysicalTracks()
        if self.tracks is not None:
            self.tracks.reset()
        if self.__vEntity.model is not None and self.__vEntity.model is not None:
            self.shadowManager.unregisterCompoundModel(self.__vEntity.model)
        self.shadowManager = None
        self.undamagedStateChildren = []
        self.reset()
        self.shadowManager = VehicleShadowManager()
        self.shadowManager.updatePlayerTarget(None)
        if outfit.style and outfit.style.isProgression:
            outfit = self.__getStyleProgressionOutfitData(outfit)
        self.__outfit = outfit
        self.__startBuild(vDesc, vState)
        return

    def __startBuild(self, vDesc, vState):
        self.__curBuildInd += 1
        self.__vState = vState
        self.__resources = {}
        self.__vehicleStickers = None
        cfg = hangarCFG()
        if vState == 'undamaged':
            self.__currentEmblemsAlpha = cfg['emblems_alpha_undamaged']
            self.__isVehicleDestroyed = False
        else:
            self.__currentEmblemsAlpha = cfg['emblems_alpha_damaged']
            self.__isVehicleDestroyed = True
        self.__vDesc = vDesc
        resources = camouflages.getCamoPrereqs(self.__outfit, vDesc)
        if not self.__isVehicleDestroyed:
            self.__attachments = camouflages.getAttachments(self.__outfit, vDesc)
        modelsSet = self.__outfit.modelsSet
        splineDesc = vDesc.chassis.splineDesc
        if splineDesc is not None:
            for _, trackDesc in splineDesc.trackPairs.iteritems():
                resources += trackDesc.prerequisites(modelsSet)

        from vehicle_systems import model_assembler
        resources.append(model_assembler.prepareCompoundAssembler(self.__vDesc, ModelsSetParams(modelsSet, self.__vState, self.__attachments), self.__spaceId))
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.VEHICLE_LOADING, ctx={'started': True,
         'vEntityId': self.__vEntity.id,
         'intCD': self.__vDesc.type.compactDescr}), scope=EVENT_BUS_SCOPE.DEFAULT)
        cfg = hangarCFG()
        gunScale = cfg.get('cam_capsule_gun_scale', _CAMERA_CAPSULE_GUN_SCALE)
        capsuleScale = cfg.get('cam_capsule_scale', _CAMERA_CAPSULE_SCALE)
        hitTesterManagers = {TankPartNames.CHASSIS: vDesc.chassis.hitTesterManager,
         TankPartNames.HULL: vDesc.hull.hitTesterManager,
         TankPartNames.TURRET: vDesc.turret.hitTesterManager,
         TankPartNames.GUN: vDesc.gun.hitTesterManager}
        bspModels = ()
        crashedBspModels = ()
        for partName, htManager in hitTesterManagers.iteritems():
            partId = TankPartNames.getIdx(partName)
            bspModel = (partId, htManager.modelHitTester.bspModelName)
            bspModels = bspModels + (bspModel,)
            if htManager.crashedModelHitTester:
                crashedBspModel = (partId, htManager.crashedModelHitTester.bspModelName)
                crashedBspModels = crashedBspModels + (crashedBspModel,)

        bspModels = bspModels + ((TankPartNames.getIdx(TankPartNames.GUN) + 1,
          vDesc.hull.hitTesterManager.modelHitTester.bspModelName,
          capsuleScale,
          True), (TankPartNames.getIdx(TankPartNames.GUN) + 2,
          vDesc.turret.hitTesterManager.modelHitTester.bspModelName,
          capsuleScale,
          True), (TankPartNames.getIdx(TankPartNames.GUN) + 3,
          vDesc.gun.hitTesterManager.modelHitTester.bspModelName,
          gunScale,
          True))
        if vDesc.hull.hitTesterManager.crashedModelHitTester:
            crashedBspModels = crashedBspModels + ((TankPartNames.getIdx(TankPartNames.GUN) + 1,
              vDesc.hull.hitTesterManager.crashedModelHitTester.bspModelName,
              capsuleScale,
              True),)
        if vDesc.turret.hitTesterManager.crashedModelHitTester:
            crashedBspModels = crashedBspModels + ((TankPartNames.getIdx(TankPartNames.GUN) + 2,
              vDesc.turret.hitTesterManager.crashedModelHitTester.bspModelName,
              capsuleScale,
              True),)
        if vDesc.gun.hitTesterManager.crashedModelHitTester:
            crashedBspModels = crashedBspModels + ((TankPartNames.getIdx(TankPartNames.GUN) + 3,
              vDesc.gun.hitTesterManager.crashedModelHitTester.bspModelName,
              gunScale,
              True),)
        modelCA = BigWorld.CollisionAssembler(bspModels, self.__spaceId)
        modelCA.name = 'ModelCollisions'
        resources.append(modelCA)
        if crashedBspModels:
            crashedModelCA = BigWorld.CollisionAssembler(crashedBspModels, self.__spaceId)
            crashedModelCA.name = 'CrashedModelCollisions'
            resources.append(crashedModelCA)
        physicalTracksBuilders = vDesc.chassis.physicalTracks
        for name, builders in physicalTracksBuilders.iteritems():
            for index, builder in enumerate(builders):
                resources.append(builder.createLoader(self.__spaceId, '{0}{1}PhysicalTrack'.format(name, index), modelsSet))

        BigWorld.loadResourceListBG(tuple(resources), makeCallbackWeak(self.__onResourcesLoaded, self.__curBuildInd))
        return

    def __onResourcesLoaded(self, buildInd, resourceRefs):
        for prevGo in self.undamagedStateChildren:
            CGF.removeGameObject(prevGo)

        self.undamagedStateChildren = []
        self.removeComponentByType(GenericComponents.HierarchyComponent)
        self.removeComponentByType(GenericComponents.TransformComponent)
        self.createComponent(GenericComponents.HierarchyComponent, self.__vEntity.entityGameObject)
        self.createComponent(GenericComponents.TransformComponent, Math.Vector3(0, 0, 0))
        if not self.__vDesc:
            self.__fireResourcesLoadedEvent()
            return
        elif buildInd != self.__curBuildInd:
            return
        else:
            failedIDs = resourceRefs.failedIDs
            resources = self.__resources
            succesLoaded = True
            for resID, resource in resourceRefs.items():
                if resID not in failedIDs:
                    resources[resID] = resource
                _logger.error('Could not load %s', resID)
                succesLoaded = False

            if self.collisions:
                BigWorld.removeCameraCollider(self.collisions.getColliderID())
            self._modelCollisions = resourceRefs['ModelCollisions']
            hasCrashedCollisions = resourceRefs.has_key('CrashedModelCollisions')
            if hasCrashedCollisions:
                self._crashedModelCollisions = resourceRefs['CrashedModelCollisions']
            if self.__isVehicleDestroyed and hasCrashedCollisions:
                self.collisions = self.createComponent(BigWorld.CollisionComponent, self._crashedModelCollisions)
            else:
                self.collisions = self.createComponent(BigWorld.CollisionComponent, self._modelCollisions)
            if succesLoaded:
                self.__setupModel(buildInd)
            if self.turretRotator is not None:
                self.turretRotator.destroy()
            self.turretRotator = SimpleTurretRotator(self.compoundModel, self.__staticTurretYaw, self.__vDesc.hull.turretPositions[0], self.__vDesc.hull.turretPitches[0], easingCls=math_utils.Easing.squareEasing)
            self.__applyAttachmentsVisibility()
            self.__fireResourcesLoadedEvent()
            if succesLoaded:
                self.__doFinalSetup(buildInd)
            super(HangarVehicleAppearance, self).activate()
            return

    def __fireResourcesLoadedEvent(self):
        compDescr = self.__vDesc.type.compactDescr if self.__vDesc is not None else None
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.VEHICLE_LOADING, ctx={'started': False,
         'vEntityId': self.__vEntity.id,
         'intCD': compDescr}), scope=EVENT_BUS_SCOPE.DEFAULT)
        return

    def __onAnimatorsLoaded(self, buildInd, outfit, resourceRefs):
        if not self.__vDesc:
            return
        if buildInd != self.__curBuildInd:
            return
        self.__clearModelAnimators()
        self.__modelAnimators = camouflages.getModelAnimators(outfit, self.__vDesc, self.__spaceId, resourceRefs, self.compoundModel)
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(True)
            modelAnimator.animator.start()

        if not self.__isVehicleDestroyed:
            self.__modelAnimators.extend(camouflages.getAttachmentsAnimators(self.__attachments, self.__spaceId, resourceRefs, self.compoundModel))
        from vehicle_systems import model_assembler
        model_assembler.assembleCustomLogicComponents(self, self.__vEntity.typeDescriptor, self.__attachments, self.__modelAnimators)
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.start()

    def __onSettingsChanged(self, diff):
        if 'showMarksOnGun' in diff:
            self.__showMarksOnGun = not diff['showMarksOnGun']
            self.refresh()

    def _getActiveOutfit(self, vDesc):
        if g_currentPreviewVehicle.isPresent() and not g_currentPreviewVehicle.isHeroTank:
            vehicleCD = g_currentPreviewVehicle.item.descriptor.makeCompactDescr()
            return self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
        elif not g_currentVehicle.isPresent():
            if vDesc is not None:
                vehicleCD = vDesc.makeCompactDescr()
                outfit = self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
            else:
                _logger.error('Failed to get base vehicle outfit. VehicleDescriptor is None.')
                outfit = self.itemsFactory.createOutfit()
            return outfit
        else:
            vehicle = g_currentVehicle.item
            season = g_tankActiveCamouflage.get(vehicle.intCD, vehicle.getAnyOutfitSeason())
            g_tankActiveCamouflage[vehicle.intCD] = season
            outfit = vehicle.getOutfit(season)
            if not outfit:
                vehicleCD = vehicle.descriptor.makeCompactDescr()
                outfit = self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
            return outfit

    def __assembleModel(self):
        from vehicle_systems import model_assembler
        resources = self.__resources
        self.__vEntity.model = resources[self.__vDesc.name]
        if not self.__isVehicleDestroyed:
            self.__fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion())
            model_assembler.setupTracksFashion(self.__vDesc, self.__fashions.chassis)
            self.__vEntity.model.setupFashions(self.__fashions)
            model_assembler.assembleCollisionObstaclesCollector(self, None, self.__vDesc)
            model_assembler.assembleTessellationCollisionSensor(self, None)
            wheelsScroll = None
            wheelsSteering = None
            if self.__vDesc.chassis.generalWheelsAnimatorConfig is not None:
                scrollableWheelsCount = self.__vDesc.chassis.generalWheelsAnimatorConfig.getWheelsCount()
                wheelsScroll = [ (lambda : 0.0) for _ in xrange(scrollableWheelsCount) ]
                steerableWheelsCount = self.__vDesc.chassis.generalWheelsAnimatorConfig.getSteerableWheelsCount()
                wheelsSteering = [ (lambda : 0.0) for _ in xrange(steerableWheelsCount) ]
            chassisFashion = self.__fashions.chassis
            splineTracksImpl = model_assembler.setupSplineTracks(chassisFashion, self.__vDesc, self.__vEntity.model, self.__resources, self.__outfit.modelsSet)
            self.wheelsAnimator = model_assembler.createWheelsAnimator(self, ColliderTypes.VEHICLE_COLLIDER, self.__vDesc, lambda : 0, wheelsScroll, wheelsSteering, splineTracksImpl)
            self.trackNodesAnimator = model_assembler.createTrackNodesAnimator(self, self.__vDesc)
            model_assembler.assembleTracks(self.__resources, self.__vDesc, self, splineTracksImpl, True)
            dirtEnabled = BigWorld.WG_dirtEnabled() and 'HD' in self.__vDesc.type.tags
            if dirtEnabled:
                dirtHandlers = [BigWorld.PyDirtHandler(True, self.__vEntity.model.node(TankPartNames.CHASSIS).position.y),
                 BigWorld.PyDirtHandler(False, self.__vEntity.model.node(TankPartNames.HULL).position.y),
                 BigWorld.PyDirtHandler(False, self.__vEntity.model.node(TankPartNames.TURRET).position.y),
                 BigWorld.PyDirtHandler(False, self.__vEntity.model.node(TankPartNames.GUN).position.y)]
                modelHeight, _ = self.computeVehicleHeight()
                self.dirtComponent = self.createComponent(Vehicular.DirtComponent, dirtHandlers, modelHeight)
                for fashionIdx, _ in enumerate(TankPartNames.ALL):
                    self.__fashions[fashionIdx].addMaterialHandler(dirtHandlers[fashionIdx])

                self.dirtComponent.setBase()
            outfitData = camouflages.getOutfitData(self, self.__outfit, self.__vDesc, self.__vState != 'undamaged')
            self.c11nComponent = self.createComponent(Vehicular.C11nEditComponent, self.__fashions, self.compoundModel, outfitData)
            if self.__outfit.style and self.__outfit.style.isProgression:
                self.__updateStyleProgression(self.__outfit)
            self.__updateDecals(self.__outfit)
            self.__updateSequences(self.__outfit)
        else:
            self.__fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion(), BigWorld.WGBaseFashion())
            self.__vEntity.model.setupFashions(self.__fashions)
            self.wheelsAnimator = None
            self.trackNodesAnimator = None
            self.dirtComponent = None
            self.flagComponent = None
        self.__staticTurretYaw = self.__vDesc.gun.staticTurretYaw
        self.__staticGunPitch = self.__vDesc.gun.staticPitch
        if not ('AT-SPG' in self.__vDesc.type.tags or 'SPG' in self.__vDesc.type.tags):
            if self.__staticTurretYaw is None:
                self.__staticTurretYaw = self._getTurretYaw()
                turretYawLimits = self.__vDesc.gun.turretYawLimits
                if turretYawLimits is not None:
                    self.__staticTurretYaw = math_utils.clamp(turretYawLimits[0], turretYawLimits[1], self.__staticTurretYaw)
            if self.__staticGunPitch is None:
                self.__staticGunPitch = self._getGunPitch()
                gunPitchLimits = self.__vDesc.gun.pitchLimits['absolute']
                self.__staticGunPitch = math_utils.clamp(gunPitchLimits[0], gunPitchLimits[1], self.__staticGunPitch)
        else:
            if self.__staticTurretYaw is None:
                self.__staticTurretYaw = 0.0
            if self.__staticGunPitch is None:
                self.__staticGunPitch = 0.0
        gunPitchMatrix = math_utils.createRotationMatrix((0.0, self.__staticGunPitch, 0.0))
        self.__setGunMatrix(gunPitchMatrix)
        return

    def __onItemsCacheSyncCompleted(self, updateReason, _):
        if updateReason == CACHE_SYNC_REASON.DOSSIER_RESYNC and self.__vehicleStickers is not None and self.getThisVehicleDossierInsigniaRank() != self.__vehicleStickers.getCurrentInsigniaRank():
            self.refresh()
        return

    def getThisVehicleDossierInsigniaRank(self):
        if self.__vDesc and self.__showMarksOnGun:
            vehicleDossier = self.itemsCache.items.getVehicleDossier(self.__vDesc.type.compactDescr)
            return vehicleDossier.getRandomStats().getAchievement(MARK_ON_GUN_RECORD).getValue()

    def _requestClanDBIDForStickers(self, callback):
        BigWorld.player().stats.get('clanDBID', callback)

    def __onClanDBIDRetrieved(self, _, clanID):
        if self.__vehicleStickers is not None:
            self.__vehicleStickers.setClanID(clanID)
        return

    def __setupModel(self, buildIdx):
        self.__assembleModel()
        matrix = math_utils.createSRTMatrix(Math.Vector3(1.0, 1.0, 1.0), Math.Vector3(self.__vEntity.yaw, self.__vEntity.pitch, self.__vEntity.roll), self.__vEntity.position)
        self.__vEntity.model.matrix = matrix
        self.__vEntity.typeDescriptor = self.__vDesc
        typeDescr = self.__vDesc
        wheelConfig = typeDescr.chassis.generalWheelsAnimatorConfig
        if self.wheelsAnimator is not None and wheelConfig is not None:
            self.wheelsAnimator.createCollision(wheelConfig, self.collisions)
        gunColBox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN) + 3)
        center = 0.5 * (gunColBox[1] - gunColBox[0])
        gunoffset = Math.Matrix()
        gunoffset.setTranslate((0.0, 0.0, center.z + gunColBox[0].z))
        gunNode = self.__getGunNode()
        gunLink = math_utils.MatrixProviders.product(gunoffset, gunNode)
        collisionData = ((TankPartNames.getIdx(TankPartNames.CHASSIS), self.__vEntity.model.matrix),
         (TankPartNames.getIdx(TankPartNames.HULL), self.__vEntity.model.node(TankPartNames.HULL)),
         (TankPartNames.getIdx(TankPartNames.TURRET), self.__vEntity.model.node(TankPartNames.TURRET)),
         (TankPartNames.getIdx(TankPartNames.GUN), gunNode))
        self.collisions.connect(self.__vEntity.id, ColliderTypes.VEHICLE_COLLIDER, collisionData)
        collisionData = ((TankPartNames.getIdx(TankPartNames.GUN) + 1, self.__vEntity.model.node(TankPartNames.HULL)), (TankPartNames.getIdx(TankPartNames.GUN) + 2, self.__vEntity.model.node(TankPartNames.TURRET)), (TankPartNames.getIdx(TankPartNames.GUN) + 3, gunLink))
        self.collisions.connect(self.__vEntity.id, self._getColliderType(), collisionData)
        self._reloadColliderType(self.__vEntity.state)
        self.__reloadShadowManagerTarget(self.__vEntity.state)
        return

    def _getColliderType(self):
        return ColliderTypes.HANGAR_VEHICLE_COLLIDER

    def __handleEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['entityId'] == self.__vEntity.id:
            self._reloadColliderType(ctx['state'])
            self.__reloadShadowManagerTarget(ctx['state'])

    def _reloadColliderType(self, state):
        if not self.collisions:
            return
        if state != CameraMovementStates.FROM_OBJECT:
            colliderData = (self.collisions.getColliderID(), (TankPartNames.getIdx(TankPartNames.GUN) + 1, TankPartNames.getIdx(TankPartNames.GUN) + 2, TankPartNames.getIdx(TankPartNames.GUN) + 3))
            BigWorld.appendCameraCollider(colliderData)
            cameraManager = CGF.getManager(self.__spaceId, HangarCameraManager)
            if cameraManager:
                cfg = hangarCFG()
                minDistFactor = cfg.get('cam_min_dist_vehicle_hull_length_k', _CAMERA_MIN_DIST_FACTOR)
                cameraManager.setMinDist(minDistFactor * self.computeVehicleLength())
        else:
            BigWorld.removeCameraCollider(self.collisions.getColliderID())

    def __reloadShadowManagerTarget(self, state):
        if not self.shadowManager or not self.__vEntity.model:
            return
        else:
            self.shadowManager.registerCompoundModel(self.__vEntity.model)
            if state == CameraMovementStates.ON_OBJECT:
                self.shadowManager.updatePlayerTarget(self.__vEntity.model)
            elif state == CameraMovementStates.MOVING_TO_OBJECT:
                self.shadowManager.updatePlayerTarget(None)
            return

    def __doFinalSetup(self, buildIdx):
        if buildIdx != self.__curBuildInd:
            return
        else:
            self.__loadState.load()
            if self.__onLoadedCallback is not None:
                self.__onLoadedCallback()
                self.__onLoadedCallback = None
            if self.__onLoadedAfterRefreshCallback is not None:
                self.__onLoadedAfterRefreshCallback()
                self.__onLoadedAfterRefreshCallback = None
            if self.__vDesc is not None and 'observer' in self.__vDesc.type.tags:
                self.__vEntity.model.visible = False
            return

    def __applyAttachmentsVisibility(self):
        if self.compoundModel is None:
            return False
        else:
            partHandleNotFoundErrorCode = 4294967295L
            for attachment in self.__attachments:
                if attachment.partNodeAlias is None:
                    continue
                partNode = self.compoundModel.node(attachment.partNodeAlias)
                if partNode is None:
                    _logger.error('Attachment node "%s" is not found.', attachment.partNodeAlias)
                    continue
                partId = self.compoundModel.findPartHandleByNode(partNode)
                if partId == partHandleNotFoundErrorCode:
                    _logger.error('Part handle is not found, see node "%s"', attachment.partNodeAlias)
                    continue
                if not attachment.initialVisibility:
                    self.compoundModel.setPartVisible(partId, False)

            return True

    def getAnchorParams(self, slotId, areaId, regionIdx):
        if self.__anchorsParams is None:
            self.__initAnchorsParams()
        anchorParams = self.__anchorsParams.get(slotId, {}).get(areaId, {}).get(regionIdx)
        return anchorParams

    def updateAnchorsParams(self, tankPartsToUpdate=TankPartIndexes.ALL):
        if self.__anchorsHelpers is None or self.__anchorsParams is None:
            return
        else:
            self.__updateAnchorsParams(tankPartsToUpdate)
            return

    def getCentralPointForArea(self, areaIdx):

        def _getBBCenter(tankPartName):
            partIdx = TankPartNames.getIdx(tankPartName)
            boundingBox = Math.Matrix(self.__vEntity.model.getBoundsForPart(partIdx))
            bbCenter = boundingBox.applyPoint((0.5, 0.5, 0.5))
            return bbCenter

        if areaIdx == ApplyArea.HULL:
            trackLeftUpFront = self.__vEntity.model.node('HP_TrackUp_LFront').position
            trackRightUpRear = self.__vEntity.model.node('HP_TrackUp_RRear').position
            position = (trackLeftUpFront + trackRightUpRear) / 2.0
            bbCenter = _getBBCenter(TankPartNames.HULL)
            turretJointPosition = self.__vEntity.model.node('HP_turretJoint').position
            position.y = min(turretJointPosition.y, bbCenter.y)
        elif areaIdx == ApplyArea.TURRET:
            position = _getBBCenter(TankPartNames.TURRET)
            position.y = self.__vEntity.model.node('HP_gunJoint').position.y
        elif areaIdx == ApplyArea.GUN_2:
            position = self.__vEntity.model.node('HP_gunJoint').position
        elif areaIdx == ApplyArea.GUN:
            gunJointPos = self.__vEntity.model.node('HP_gunJoint').position
            gunFirePos = self.__vEntity.model.node('HP_gunFire').position
            position = (gunFirePos + gunJointPos) / 2.0
        else:
            position = _getBBCenter(TankPartNames.CHASSIS)
        return position

    def __applyCustomization(self, outfit, callback):
        if outfit.style and outfit.style.isProgression:
            outfit = self.__getStyleProgressionOutfitData(outfit)
            self.__updateStyleProgression(outfit)
        self.__updateCamouflage(outfit)
        self.__updatePaint(outfit)
        self.__updateDecals(outfit)
        self.__updateProjectionDecals(outfit)
        self.__updateSequences(outfit)
        if callback is not None:
            callback()
        return

    def updateCustomization(self, outfit=None, callback=None):
        if self.__isVehicleDestroyed:
            return
        else:
            if g_currentVehicle.item:
                vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
            else:
                vehicleCD = g_currentPreviewVehicle.item.descriptor.makeCompactDescr()
            outfit = outfit or self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
            if self.recreateRequired(outfit):
                self.refresh(outfit, callback)
                return
            if self.c11nComponent is None:
                self.__onLoadedAfterRefreshCallback = partial(self.__applyCustomization, outfit, callback)
                return
            self.__applyCustomization(outfit, None)
            return

    def rotateTurretForAnchor(self, anchorId, duration=EASING_TRANSITION_DURATION):
        if self.compoundModel is None or self.__vDesc is None:
            return False
        else:
            defaultYaw = self._getTurretYaw()
            turretYaw = self.__getTurretYawForAnchor(anchorId, defaultYaw)
            self.turretRotator.start(turretYaw, rotationTime=duration)
            return

    def rotateGunToDefault(self):
        if self.compoundModel is None:
            return False
        else:
            localGunMatrix = self.__getGunNode().local
            currentGunPitch = localGunMatrix.pitch
            gunPitchAngle = self._getGunPitch()
            if abs(currentGunPitch - gunPitchAngle) < 0.0001:
                return False
            gunPitchMatrix = math_utils.createRotationMatrix((0.0, gunPitchAngle, 0.0))
            self.__setGunMatrix(gunPitchMatrix)
            return True

    def getVehicleCentralPoint(self):
        hullAABB = self.collisions.getBoundingBox(TankPartIndexes.HULL)
        centralPoint = Math.Vector3((hullAABB[1].x + hullAABB[0].x) / 2.0, hullAABB[1].y / 2.0, (hullAABB[1].z + hullAABB[0].z) / 2.0)
        return centralPoint

    def __getAnchorHelperById(self, anchorId):
        if anchorId.slotType not in self.__anchorsHelpers:
            return None
        else:
            slotTypeAnchorHelpers = self.__anchorsHelpers[anchorId.slotType]
            if anchorId.areaId not in slotTypeAnchorHelpers:
                return None
            areaAnchorHelpers = slotTypeAnchorHelpers[anchorId.areaId]
            return None if anchorId.regionIdx not in areaAnchorHelpers else areaAnchorHelpers[anchorId.regionIdx]

    def __updateAnchorHelperWithId(self, anchorId, newAnchorHelper):
        self.__anchorsHelpers[anchorId.slotType][anchorId.areaId][anchorId.regionIdx] = newAnchorHelper

    def __getTurretYawForAnchor(self, anchorId, defaultYaw):
        turretYaw = defaultYaw
        if anchorId is not None and hasTurretRotator(self.__vDesc):
            anchorHelper = self.__getAnchorHelperById(anchorId)
            if anchorHelper is not None:
                if anchorHelper.turretYaw is not None:
                    turretYaw = anchorHelper.turretYaw
                else:
                    if anchorHelper.attachedPartIdx == TankPartIndexes.HULL:
                        needsCorrection = anchorId.slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION) or anchorId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL and anchorHelper.descriptor.showOn == ApplyArea.HULL
                        if needsCorrection:
                            turretYaw = self.__correctTurretYaw(anchorHelper, defaultYaw)
                    anchorHelper = AnchorHelper(anchorHelper.location, anchorHelper.descriptor, turretYaw, anchorHelper.partIdx, anchorHelper.attachedPartIdx)
                    self.__updateAnchorHelperWithId(anchorId, anchorHelper)
        turretYawLimits = self.__vDesc.gun.turretYawLimits
        if turretYawLimits is not None:
            turretYaw = math_utils.clamp(turretYawLimits[0], turretYawLimits[1], turretYaw)
        return turretYaw

    def __updatePaint(self, outfit):
        for fashionIdx, _ in enumerate(TankPartNames.ALL):
            repaint = camouflages.getRepaint(outfit, fashionIdx, self.__vDesc)
            self.c11nComponent.setPartPaint(fashionIdx, repaint)

    def __updateCamouflage(self, outfit):
        for fashionIdx, descId in enumerate(TankPartNames.ALL):
            camo = camouflages.getCamo(self, outfit, fashionIdx, self.__vDesc, descId, self.__vState != 'undamaged')
            self.c11nComponent.setPartCamo(fashionIdx, camo)

    def __updateDecals(self, outfit):
        if self.__vehicleStickers is not None:
            self.__vehicleStickers.detach()
        self.__vehicleStickers = VehicleStickers.VehicleStickers(self.__spaceId, self.__vDesc, self.getThisVehicleDossierInsigniaRank(), outfit)
        self.__vehicleStickers.alpha = self.__currentEmblemsAlpha
        self.__vehicleStickers.attach(self.__vEntity.model, self.__isVehicleDestroyed, False)
        self._requestClanDBIDForStickers(self.__onClanDBIDRetrieved)
        return

    def __updateProjectionDecals(self, outfit):
        decals = camouflages.getGenericProjectionDecals(outfit, self.__vDesc)
        self.c11nComponent.setDecals(decals)

    def __updateSequences(self, outfit):
        resources = camouflages.getModelAnimatorsPrereqs(outfit, self.__spaceId)
        resources.extend(camouflages.getAttachmentsAnimatorsPrereqs(self.__attachments, self.__spaceId))
        if not resources:
            self.__clearModelAnimators()
            if not self.__isVehicleDestroyed:
                from vehicle_systems import model_assembler
                model_assembler.assembleCustomLogicComponents(self, self.__vEntity.typeDescriptor, self.__attachments, self.__modelAnimators)
            return
        BigWorld.loadResourceListBG(tuple(resources), makeCallbackWeak(self.__onAnimatorsLoaded, self.__curBuildInd, outfit))

    def __updateStyleProgression(self, outfit):
        camouflages.changeStyleProgression(outfit.style, self, outfit.progressionLevel)

    def __clearModelAnimators(self):
        self.flagComponent = None
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.stop()

        self.__modelAnimators = []
        for go in self.undamagedStateChildren:
            CGF.removeGameObject(go)

        self.undamagedStateChildren = []
        return

    def __onVehicleChanged(self):
        self.__anchorsParams = None
        self.__anchorsHelpers = None
        return

    def __initAnchorsParams(self):
        self.__anchorsParams = {cType:{area:{} for area in Area.ALL} for cType in SLOT_TYPES}
        if self.__anchorsHelpers is None:
            self.__initAnchorsHelpers()
        self.__updateAnchorsParams(TankPartIndexes.ALL)
        return

    def __updateAnchorsParams(self, tankPartsToUpdate):
        tankPartsMatrices = {}
        for tankPartIdx in TankPartIndexes.ALL:
            tankPartName = TankPartIndexes.getName(tankPartIdx)
            tankPartsMatrices[tankPartIdx] = Math.Matrix(self.__vEntity.model.node(tankPartName))

        for slotType in SLOT_TYPES:
            for areaId in Area.ALL:
                anchorHelpers = self.__anchorsHelpers[slotType][areaId]
                for regionIdx, anchorHelper in anchorHelpers.iteritems():
                    attachedPartIdx = anchorHelper.attachedPartIdx
                    if attachedPartIdx not in tankPartsToUpdate:
                        continue
                    anchorLocationWS = self.__getAnchorLocationWS(anchorHelper.location, anchorHelper.partIdx)
                    self.__anchorsParams[slotType][areaId][regionIdx] = AnchorParams(anchorLocationWS, anchorHelper.descriptor, AnchorId(slotType, areaId, regionIdx))

    def __initAnchorsHelpers(self):
        anchorsHelpers = {cType:{area:{} for area in Area.ALL} for cType in SLOT_TYPES}
        for slotType in SLOT_TYPES:
            for areaId in Area.ALL:
                for regionIdx, anchor in g_currentVehicle.item.getAnchors(slotType, areaId):
                    if isinstance(anchor, EmblemSlot):
                        getAnchorHelper = self.__getEmblemAnchorHelper
                    elif isinstance(anchor, BaseCustomizationSlot):
                        getAnchorHelper = self.__getAnchorHelper
                    else:
                        continue
                    anchorsHelpers[slotType][areaId][regionIdx] = getAnchorHelper(anchor)

        self.__anchorsHelpers = anchorsHelpers

    def __getEmblemAnchorHelper(self, anchor):
        startPos = anchor.rayStart
        endPos = anchor.rayEnd
        normal = startPos - endPos
        normal.normalise()
        up = normal * (anchor.descriptor.rayUp * normal)
        up.normalise()
        position = startPos + (endPos - startPos) * 0.5
        anchorLocation = AnchorLocation(position, normal, up)
        partIdx = anchor.areaId
        attachedPartIdx = self.__getAttachedPartIdx(position, normal, partIdx)
        return AnchorHelper(anchorLocation, anchor.descriptor, None, partIdx, attachedPartIdx)

    def __getAnchorHelper(self, anchor):
        slotType = ANCHOR_TYPE_TO_SLOT_TYPE_MAP[anchor.descriptor.type]
        if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            partIdx = TankPartIndexes.CHASSIS
            ypr = anchor.rotation
            rotationMatrix = Math.Matrix()
            rotationMatrix.setRotateYPR((ypr.y, ypr.x, ypr.z))
            normal = rotationMatrix.applyVector((0, -1, 0))
            normal.normalise()
            up = rotationMatrix.applyVector((0, 0, -1))
            up.normalise()
            position = Math.Vector3(anchor.position) + anchor.descriptor.anchorShift * normal
        else:
            if slotType in (GUI_ITEM_TYPE.MODIFICATION, GUI_ITEM_TYPE.STYLE):
                partIdx = TankPartIndexes.HULL
                position = self.getVehicleCentralPoint()
            else:
                partIdx = anchor.areaId
                position = anchor.anchorPosition
            normal = anchor.anchorDirection
            normal.normalise()
            up = normal * (Math.Vector3(0, 1, 0) * normal)
            up.normalise()
        anchorLocation = AnchorLocation(position, normal, up)
        attachedPartIdx = self.__getAttachedPartIdx(position, normal, partIdx)
        return AnchorHelper(anchorLocation, anchor.descriptor, None, partIdx, attachedPartIdx)

    def __getAttachedPartIdx(self, position, normal, tankPartIdx):
        partMatrix = Math.Matrix(self.__vEntity.model.node(TankPartIndexes.getName(tankPartIdx)))
        startPos = position + normal * 0.1
        endPos = position - normal * 0.6
        startPos = partMatrix.applyPoint(startPos)
        endPos = partMatrix.applyPoint(endPos)
        collisions = self.collisions.collideAllWorld(startPos, endPos)
        if collisions is not None:
            for collision in collisions:
                partIdx = collision[3]
                if partIdx in TankPartIndexes.ALL:
                    return partIdx

        return tankPartIdx

    def __correctTurretYaw(self, anchorHelper, defaultYaw):
        if not _SHOULD_CHECK_DECAL_UNDER_GUN:
            return defaultYaw
        else:
            partMatrix = Math.Matrix(self.__vEntity.model.node(TankPartIndexes.getName(anchorHelper.partIdx)))
            turretMat = Math.Matrix(self.compoundModel.node(TankPartNames.TURRET))
            transformMatrix = math_utils.createRTMatrix((turretMat.yaw, partMatrix.pitch, partMatrix.roll), partMatrix.translation)
            anchorLocationWS = self.__applyToAnchorLocation(anchorHelper.location, transformMatrix)
            position = anchorLocationWS.position
            direction = anchorLocationWS.normal
            up = anchorLocationWS.up
            fromTurretToHit = position - turretMat.translation
            if fromTurretToHit.dot(turretMat.applyVector((0, 0, 1))) < 0:
                return defaultYaw
            checkDirWorld = direction * 10.0
            cornersWorldSpace = self.__getDecalCorners(position, direction, up, anchorHelper.descriptor)
            if cornersWorldSpace is None:
                return defaultYaw
            slotType = ANCHOR_TYPE_TO_SLOT_TYPE_MAP[anchorHelper.descriptor.type]
            if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                turretLeftDir = turretMat.applyVector((1, 0, 0))
                turretLeftDir.normalise()
                gunJoin = self.__vEntity.model.node('HP_gunJoint')
                fromGunJointToAnchor = gunJoin.position - position
                decalDiags = (cornersWorldSpace[0] - cornersWorldSpace[2], cornersWorldSpace[1] - cornersWorldSpace[3])
                fromGunToHit = abs(fromGunJointToAnchor.dot(turretLeftDir))
                halfDecalWidth = max((abs(decalDiag.dot(turretLeftDir)) for decalDiag in decalDiags)) * 0.5
                if fromGunToHit > halfDecalWidth * _PROJECTION_DECAL_OVERLAPPING_FACTOR:
                    return defaultYaw
            result = self.collisions.collideShape(TankPartIndexes.GUN, cornersWorldSpace, checkDirWorld)
            if result < 0.0:
                return defaultYaw
            turretYaw = _HANGAR_TURRET_SHIFT
            gunDir = turretMat.applyVector(Math.Vector3(0, 0, 1))
            if Math.Vector3(0, 1, 0).dot(gunDir * fromTurretToHit) > 0.0:
                turretYaw = -turretYaw
            return turretYaw

    def __getDecalCorners(self, position, direction, up, slotDescriptor):
        slotType = ANCHOR_TYPE_TO_SLOT_TYPE_MAP[slotDescriptor.type]
        if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            width = slotDescriptor.scale[0]
            aspect = getProgectionDecalAspect(slotDescriptor)
            height = slotDescriptor.scale[2] * aspect
        else:
            width = slotDescriptor.size
            aspect = SLOT_ASPECT_RATIO.get(slotType)
            if aspect is not None:
                height = width * aspect
            else:
                return
        transformMatrix = Math.Matrix()
        transformMatrix.lookAt(position, direction, up)
        transformMatrix.invert()
        result = (Math.Vector3(width * 0.5, height * 0.5, 0),
         Math.Vector3(width * 0.5, -height * 0.5, 0),
         Math.Vector3(-width * 0.5, -height * 0.5, 0),
         Math.Vector3(-width * 0.5, height * 0.5, 0))
        return tuple((transformMatrix.applyPoint(vec) for vec in result))

    def __applyToAnchorLocation(self, anchorLocation, transform):
        position = transform.applyPoint(anchorLocation.position)
        normal = transform.applyVector(anchorLocation.normal)
        up = transform.applyVector(anchorLocation.up)
        if abs(normal.pitch - math.pi / 2) < 0.1:
            normal = Math.Vector3(0, -1, 0) + up * 0.01
            normal.normalise()
        return AnchorLocation(position, normal, up)

    def __getAnchorLocationWS(self, anchorLocation, partIdx):
        partMatrix = Math.Matrix(self.__vEntity.model.node(TankPartIndexes.getName(partIdx)))
        return self.__applyToAnchorLocation(anchorLocation, partMatrix)

    def __getGunNode(self):
        gunNode = self.compoundModel.node(TankNodeNames.GUN_INCLINATION)
        if gunNode is None:
            gunNode = self.compoundModel.node(TankPartNames.GUN)
        return gunNode

    def __setGunMatrix(self, gunMatrix):
        gunNode = self.__getGunNode()
        gunNode.local = gunMatrix

    @property
    def outfit(self):
        return self.__outfit

    def __getStyleProgressionOutfitData(self, outfit):
        vehicle = None
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
        elif g_currentPreviewVehicle.isPresent():
            vehicle = g_currentPreviewVehicle.item
        if vehicle:
            season = g_tankActiveCamouflage.get(vehicle.intCD, vehicle.getAnyOutfitSeason())
            progressionOutfit = camouflages.getStyleProgressionOutfit(outfit, outfit.progressionLevel, season)
            if progressionOutfit:
                return progressionOutfit
        return outfit
