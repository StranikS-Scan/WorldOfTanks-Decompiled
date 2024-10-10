# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/armory_yard_components.py
import BigWorld
import CGF
import GenericComponents
import Event
from gui.shared.utils.graphics import isRendererPipelineDeferred
from CameraComponents import CameraComponent
from cgf_components.hover_component import SelectionComponent
from cache import cached_property
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from debug_utils import LOG_ERROR
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.tankStructure import ColliderTypes

@registerComponent
class ArmoryYardCameraRuleComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory Yard Camera Rule'
    category = 'Armory Yard'
    stageCamera = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Camera', value=CGF.GameObject)


@registerComponent
class AssemblyStageVideo(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Assembly stage video'
    category = 'Armory Yard'
    videoName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Video name')


@registerComponent
class TankAssemblyPartComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Tank Assembly Part'
    category = 'Armory Yard'
    index = ComponentProperty(type=CGFMetaTypes.INT, editorName='Group index', value=1)
    visualGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Visual part', value=CGF.GameObject)
    animGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Animation part', value=CGF.GameObject)


@registerComponent
class AssemblyStageIndex(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Assembly Stage Index'
    category = 'Armory Yard'
    index = ComponentProperty(type=CGFMetaTypes.INT, editorName='Stage index')


@registerComponent
class TankAssemblyRootComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Tank Assembly Root'
    category = 'Armory Yard'


@registerComponent
class HideDetailsAfterStageComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hide details after stage'
    category = 'Armory Yard'
    toHideAfterStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To hide after stage')


@registerComponent
class HideDetailsOnStageComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hide details on stage'
    category = 'Armory Yard'
    toHideOnStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To hide on stage')


@registerComponent
class ShowDetailsAfterStageComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Show details after stage'
    category = 'Armory Yard'
    toShowAfterStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To show after stage')


@registerComponent
class HideDetailsOnPresetComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hide details on graphics preset'
    category = 'Armory Yard'
    toHideOnForward = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='To hide on forward')
    toHideOnDeferred = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='To hide on deferred')


@registerComponent
class SchemeStagesRuleComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Scheme stages rule'
    category = 'Armory Yard'
    fromStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='From stage')
    toStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To stage')


@registerComponent
class SchemeProgressionStateComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Scheme progression state'
    category = 'Armory Yard'
    stage = ComponentProperty(type=CGFMetaTypes.INT, editorName='Stage')
    progression = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Progression', value=0.0)


@registerComponent
class RecorderComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Recorder component'
    category = 'Armory Yard'
    spool1 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Spool 1', value=CGF.GameObject)
    spool2 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Spool 2', value=CGF.GameObject)
    lamp = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Lamp', value=CGF.GameObject)
    lampAnimation = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Lamp animation', value=CGF.GameObject)


@registerComponent
class HangarDetailsComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hangar Details'
    category = 'Armory Yard'
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Prefab path', value='')


@registerComponent
class ArmoryPointOfInterest(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory yard point of interest'
    category = 'Armory Yard'
    cameraName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Camera name', value='')


@registerComponent
class ArmoryCameraToPoiComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory yard camera to POI setting'
    category = 'Armory Yard'
    poiName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='POI name', value='')


@registerComponent
class ArmoryCharacterDistributionComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory yard character distribution'
    category = 'Armory Yard'
    fromStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='From stage', value=0)
    toStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To stage', value=0)


@registerComponent
class ArmoryDynamicCameraColliderComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory dynamic camera collider'
    category = 'Armory Yard'
    modelPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Model path', annotations={'path': '*.model'})


@registerComponent
class AssemblyStageXrayComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Assembly stage xray'
    category = 'Armory Yard'


@registerComponent
class ArmoryHullXrayAnimationComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory hull xray animation'
    category = 'Armory Yard'
    openName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Open anim layer name', value='')
    closeName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Close anim layer name', value='')


def partAnimatorComponent(part):
    partComponent = part.findComponentByType(TankAssemblyPartComponent)
    return (partComponent, partComponent.animGO.findComponentByType(GenericComponents.AnimatorComponent)) if partComponent is not None else (None, None)


class AssemblyStageIndexManager(CGF.ComponentManager):

    def __init__(self):
        super(AssemblyStageIndexManager, self).__init__()
        self.__rootObject = None
        self.__eventManager = Event.EventManager()
        self.onReady = Event.SafeEvent(self.__eventManager)
        self.__stageIndexToStageGO = {}
        self.__stageGroupParts = {}
        self.__stageGroupDuration = {}
        self.__stageVideo = {}
        self.__toHideListAfterStageGO = []
        self.__toHideListOnStageGO = []
        self.__toShowListAfterStageGO = []
        self.__stageCameras = {}
        self.__cameraToPOI = {}
        self.__pointsOfInterest = []
        self.__hangarDetailsGO = None
        self.__hangarDetailsPath = ''
        self.__hangarDetailsPos = None
        self.__recorderGO = None
        self.__schemeStageRange = None
        self.__schemeGO = None
        self.__schemeProgressionStates = {}
        self.__hullXrayGO = None
        return

    @onRemovedQuery(TankAssemblyRootComponent, CGF.GameObject)
    def onRemoved(self, rootComponent, gameObject):
        self.__stageIndexToStageGO = {}
        self.__stageGroupParts = {}
        self.__stageGroupDuration = {}
        self.__stageVideo = {}
        self.__toHideListAfterStageGO = []
        self.__toHideListOnStageGO = []
        self.__toShowListAfterStageGO = []
        self.__stageCameras = {}
        self.__cameraToPOI = {}
        self.__pointsOfInterest = []
        self.__rootObject = None
        self.__hangarDetailsGO = None
        self.__hangarDetailsPath = ''
        self.__hangarDetailsPos = None
        self.__recorderGO = None
        self.__schemeStageRange = None
        self.__schemeGO = None
        self.__schemeProgressionStates = {}
        self.__hullXrayGO = None
        self.__eventManager.clear()
        return

    @onAddedQuery(ArmoryPointOfInterest, CGF.GameObject)
    def onAddedPOI(self, poiComponent, gameObject):
        self.__pointsOfInterest.append((poiComponent.cameraName, gameObject))

    @onAddedQuery(HideDetailsAfterStageComponent, CGF.GameObject)
    def onAddedHideDetailsAfterStageComponent(self, hideComponent, gameObject):
        self.__toHideListAfterStageGO.append((hideComponent.toHideAfterStage, gameObject))

    @onAddedQuery(HideDetailsOnStageComponent, CGF.GameObject)
    def onAddedHideDetailsOnStageComponent(self, hideComponent, gameObject):
        self.__toHideListOnStageGO.append((hideComponent.toHideOnStage, gameObject))

    @onAddedQuery(HideDetailsOnPresetComponent, CGF.GameObject)
    def onAddedHideDetailsOnPresetComponent(self, hideComponent, gameObject):
        deferred = isRendererPipelineDeferred()
        if hideComponent.toHideOnDeferred and deferred or hideComponent.toHideOnForward and not deferred:
            CGF.removeGameObject(gameObject)

    @onAddedQuery(ShowDetailsAfterStageComponent, CGF.GameObject)
    def onAddedShowDetailsAfterStageComponent(self, showComponent, gameObject):
        self.__toShowListAfterStageGO.append((showComponent.toShowAfterStage, gameObject))

    @onAddedQuery(ArmoryYardCameraRuleComponent, AssemblyStageIndex, CGF.GameObject)
    def onAddedCameraRule(self, cameraRuleComponent, stageComponent, go):
        cameraComponent = cameraRuleComponent.stageCamera.findComponentByType(CameraComponent)
        if cameraComponent is not None:
            self.__stageCameras[stageComponent.index] = cameraComponent.name
        return

    @onAddedQuery(ArmoryCameraToPoiComponent, CameraComponent, CGF.GameObject)
    def onAddedCameraToPoiComponent(self, cameraToPoiComponent, cameraComponent, go):
        self.__cameraToPOI[cameraComponent.name] = cameraToPoiComponent.poiName

    @onAddedQuery(SchemeStagesRuleComponent, CGF.GameObject)
    def onAddedSchemeStagesRule(self, schemeComponent, gameObject):
        self.__schemeGO = gameObject
        self.__schemeStageRange = (schemeComponent.fromStage, schemeComponent.toStage)
        animatorComponent = gameObject.findComponentByType(GenericComponents.AnimatorComponent)
        if animatorComponent is None:
            return
        else:
            for stage in range(schemeComponent.fromStage, schemeComponent.toStage + 1):
                self.__stageGroupDuration[stage] = {}
                self.__stageGroupDuration[stage].update({0: None})
                duration = animatorComponent.getDuration(stage - 1)
                self.__stageGroupDuration[stage][0] = max(self.__stageGroupDuration[stage][0], duration)

            return

    @onAddedQuery(ArmoryHullXrayAnimationComponent, GenericComponents.DynamicModelComponent, GenericComponents.AnimatorComponent, CGF.GameObject)
    def onAddedHullXrayAnimation(self, xrayComponent, dynModelComponent, animatorComponent, go):
        if xrayComponent.openName == '' or xrayComponent.closeName == '':
            LOG_ERROR('GO {} : ArmoryHullXrayAnimationComponent has empty layer names!'.format(go.name))
            return
        self.__hullXrayGO = go

    @onAddedQuery(ArmoryDynamicCameraColliderComponent, CGF.GameObject)
    def onAddedCollider(self, colliderComponent, go):
        modelName = colliderComponent.modelPath
        collisionModels = ((0, modelName),)
        collisionAssembler = BigWorld.CollisionAssembler(collisionModels, self.spaceID)
        BigWorld.loadResourceListBG((collisionAssembler,), makeCallbackWeak(self.__onCollisionsLoaded, go))

    def __onCollisionsLoaded(self, gameObject, resourceRefs):
        if gameObject.findComponentByType(BigWorld.CollisionComponent) is None:
            collisionComponent = gameObject.createComponent(BigWorld.CollisionComponent, resourceRefs['collisionAssembler'])
            transformComponent = gameObject.findComponentByType(GenericComponents.TransformComponent)
            collisionData = ((0, transformComponent.worldTransform),)
            collisionComponent.connect(0, ColliderTypes.DYNAMIC_COLLIDER, collisionData)
            colliderData = (collisionComponent.getColliderID(), (0,))
            BigWorld.appendCameraCollider(colliderData)
        return

    @onRemovedQuery(ArmoryDynamicCameraColliderComponent, CGF.GameObject)
    def onRemovedCollider(self, colliderComponent, go):
        collisionComponent = go.findComponentByType(BigWorld.CollisionComponent)
        if collisionComponent is not None:
            BigWorld.removeCameraCollider(collisionComponent.getColliderID())
            go.removeComponent(collisionComponent)
        return

    @onAddedQuery(RecorderComponent, GenericComponents.VSEComponent, CGF.GameObject)
    def onAddedRecorder(self, recorderComp, vseComponent, gameObject):
        self.__recorderGO = gameObject

    @onAddedQuery(HangarDetailsComponent, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onAddedHangarDetails(self, detailsComponent, gameObject):
        self.__hangarDetailsGO = gameObject
        self.__hangarDetailsPath = detailsComponent.prefabPath
        transformComponent = gameObject.findComponentByType(GenericComponents.TransformComponent)
        self.__hangarDetailsPos = transformComponent.worldTransform

    @onAddedQuery(SchemeProgressionStateComponent, CGF.GameObject)
    def onAddedSchemeProgressionState(self, stateComponent, go):
        self.__schemeProgressionStates[stateComponent.stage] = stateComponent.progression

    @onAddedQuery(TankAssemblyRootComponent, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onAdded(self, rootComponent, gameObject):
        for stageGO in self.__hierarchyManager.getChildren(gameObject):
            self.processStage(stageGO)

        self.__rootObject = self.__hierarchyManager.getTopMostParent(gameObject)
        vseComponent = self.__recorderGO.findComponentByType(GenericComponents.VSEComponent)
        if vseComponent is not None:
            vseComponent.start()
        self.onReady()
        return

    def processStage(self, stageGO):
        stageIndexComponent = stageGO.findComponentByType(AssemblyStageIndex)
        if stageIndexComponent is None:
            return
        else:
            stageIndex = stageIndexComponent.index
            self.__stageIndexToStageGO[stageIndex] = stageGO
            self.__stageGroupParts[stageIndex] = {}
            self.__stageGroupDuration[stageIndex] = {}
            if self.__hierarchyManager.getChildren(stageGO) is not None:
                for child in self.__hierarchyManager.getChildren(stageGO):
                    partGroupId = 0
                    partComponent, animComponent = partAnimatorComponent(child)
                    if animComponent is not None and partComponent is not None:
                        partGroupId = partComponent.index
                        if partGroupId not in self.__stageGroupDuration[stageIndex]:
                            self.__stageGroupDuration[stageIndex].update({partGroupId: None})
                        if partGroupId not in self.__stageGroupParts[stageIndex]:
                            self.__stageGroupParts[stageIndex].update({partGroupId: []})
                        duration = animComponent.getDelay() + animComponent.getDuration() / animComponent.getSpeed()
                        self.__stageGroupDuration[stageIndex][partGroupId] = max(self.__stageGroupDuration[stageIndex][partGroupId], duration)
                        partComponent.animGO.deactivate()
                        partComponent.visualGO.deactivate()
                    self.__stageGroupParts[stageIndex][partGroupId].append(child)

            videoNameComponent = stageGO.findComponentByType(AssemblyStageVideo)
            if videoNameComponent is not None:
                self.__stageVideo[stageIndex] = videoNameComponent.videoName
            return

    def __getXrayComponents(self):
        xrayComponent = self.__hullXrayGO.findComponentByType(ArmoryHullXrayAnimationComponent)
        animatorComponent = self.__hullXrayGO.findComponentByType(GenericComponents.AnimatorComponent)
        return (xrayComponent, animatorComponent)

    def openXray(self):
        xrayComponent, animatorComponent = self.__getXrayComponents()
        if xrayComponent is not None and animatorComponent is not None:
            animatorComponent.stop()
            animatorComponent.startLayerByName(xrayComponent.openName)
            return animatorComponent.getDurationByName(xrayComponent.openName)
        else:
            return 0.0

    def closeXray(self):
        xrayComponent, animatorComponent = self.__getXrayComponents()
        if xrayComponent is not None and animatorComponent is not None:
            animatorComponent.stop()
            animatorComponent.startLayerByName(xrayComponent.closeName)
            return animatorComponent.getDurationByName(xrayComponent.closeName)
        else:
            return 0.0

    @property
    def openXrayDuration(self):
        xrayComponent, animatorComponent = self.__getXrayComponents()
        return animatorComponent.getDurationByName(xrayComponent.closeName) if xrayComponent is not None and animatorComponent is not None else 0.0

    def stageHasXray(self, stageIndex):
        if stageIndex in self.__stageIndexToStageGO:
            stageGO = self.__stageIndexToStageGO[stageIndex]
            xrayStageComponent = stageGO.findComponentByType(AssemblyStageXrayComponent)
            return xrayStageComponent is not None
        else:
            return False

    def __startSchemeStage(self, stageIndex):
        if self.__schemeGO is None:
            return
        else:
            animatorComponent = self.__schemeGO.findComponentByType(GenericComponents.AnimatorComponent)
            if animatorComponent is not None:
                animatorComponent.stop()
                animatorComponent.startLayer(stageIndex - 1)
            return

    def activateStageGroup(self, stageIndex, stageGroupId):
        if self.isSchemeStage(stageIndex):
            self.__startSchemeStage(stageIndex)
            return
        else:
            self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: animGO.activate())
            if stageIndex is not None and stageGroupId is not None:
                for part in self.__stageGroupParts[stageIndex][stageGroupId]:
                    _, animatorComponent = partAnimatorComponent(part)
                    if animatorComponent is not None:
                        animatorComponent.start()

            return

    def activateToStage(self, fromStageIndex, toStageIndex):
        for stageIndex in range(fromStageIndex, toStageIndex):
            if self.stageExists(stageIndex):
                self.__stageIndexToStageGO[stageIndex].activate()
                for stageGroupId in self.getStageSortedGroups(stageIndex):
                    self.endStageGroup(stageIndex, stageGroupId)

        lastSchemeStage = min(toStageIndex - 1, self.__schemeStageRange[1])
        self.__setSchemeProgressionState(lastSchemeStage)

    def endStageGroup(self, stageIndex, stageGroupId):
        self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: visualGO.activate(), lambda visualGO, animGO: animGO.deactivate())

    def deactivateStageGroup(self, stageIndex, stageGroupId):
        self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: visualGO.deactivate(), lambda visualGO, animGO: animGO.deactivate())

    def deactivateAllStage(self):
        for stageIndex in self.__stageIndexToStageGO:
            self.deactivateSingleStage(stageIndex)

        schemeAnimator = self.__schemeGO.findComponentByType(GenericComponents.AnimatorComponent)
        if schemeAnimator is not None:
            schemeAnimator.stop()
        self.__setSchemeProgressionState(0)
        return

    def deactivateSingleStage(self, stageIndex):
        for stageGroupId in self.__stageGroupParts[stageIndex].keys():
            self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: visualGO.deactivate(), lambda visualGO, animGO: animGO.deactivate())

    def stageExists(self, stageIndex):
        return stageIndex in self.__stageIndexToStageGO.keys()

    def stageGroupDuration(self, stageIndex, groupId):
        return self.__stageGroupDuration[stageIndex][groupId]

    def stageDuration(self, stageIndex):
        return max(self.__stageGroupDuration[stageIndex].values())

    def stageVideoName(self, stageIndex):
        return self.__stageVideo.get(stageIndex, None)

    def getRoot(self):
        return self.__rootObject

    def getStagePartGroup(self, stageIndex, groupId):
        return self.__stageGroupParts[stageIndex][groupId]

    def getStageSortedGroups(self, stageIndex):
        return sorted(self.__stageGroupParts[stageIndex])

    def stageHasDurationPart(self, stageIndex):
        return len(self.__stageGroupDuration[stageIndex]) > 0

    def tryHideUnnecessaryPartsAfterStage(self, stage):
        for toHideAfterStage, gameObject in self.__toHideListAfterStageGO:
            if toHideAfterStage <= stage:
                gameObject.deactivate()

    def tryUnhideUnnecessaryPartsAfterStage(self, stage):
        for toHideAfterStage, gameObject in self.__toHideListAfterStageGO:
            if toHideAfterStage <= stage:
                gameObject.activate()

    def tryHideUnnecessaryPartsOnStage(self, stage):
        for toHideOnStage, gameObject in self.__toHideListOnStageGO:
            if toHideOnStage <= stage:
                gameObject.deactivate()

    def tryUnhideUnnecessaryPartsOnStage(self, stage):
        for toHideOnStage, gameObject in self.__toHideListOnStageGO:
            if toHideOnStage <= stage:
                gameObject.activate()

    def showNonSequenceObjectAfterStage(self, stage):
        for toShowAfterStage, gameObject in self.__toShowListAfterStageGO:
            if toShowAfterStage == stage:
                gameObject.activate()

    def hideNonSequenceObjectAfterStage(self):
        for _, gameObject in self.__toShowListAfterStageGO:
            gameObject.deactivate()

    def __setSchemeProgressionState(self, stage):
        if self.__schemeGO is None:
            return
        else:
            modelComponent = self.__schemeGO.findComponentByType(GenericComponents.DynamicModelComponent)
            if modelComponent is not None:
                modelComponent.setMaterialParameterFloat('spawnProgeression', self.__schemeProgressionStates[stage])
            return

    def getHangarDetailsPath(self):
        return self.__hangarDetailsPath

    def getHangarDetailsGameObject(self):
        return self.__hangarDetailsGO

    def getHangarDetailsPosition(self):
        return self.__hangarDetailsPos

    def isSchemeStage(self, stage):
        return self.__schemeStageRange[0] <= stage <= self.__schemeStageRange[1]

    def getCameraDataByStageIndex(self, stageIndex):
        return self.__stageCameras[stageIndex]

    def stageIsPlaying(self, stageIndex):
        if self.isSchemeStage(stageIndex):
            animatorComponent = self.__schemeGO.findComponentByType(GenericComponents.AnimatorComponent)
            if animatorComponent is not None:
                return animatorComponent.isPlaying()
            return False
        else:
            go = self.__stageIndexToStageGO[stageIndex]
            if self.__hierarchyManager.getChildren(go) is not None:
                for child in self.__hierarchyManager.getChildren(go):
                    _, animatorComponent = partAnimatorComponent(child)
                    if animatorComponent is not None:
                        return animatorComponent.isPlaying()

            return False

    def __stageActivation(self, stageIndex, stageGroupId, *args):
        if stageIndex is not None and stageGroupId is not None:
            for part in self.__stageGroupParts[stageIndex][stageGroupId]:
                partComponent, _ = partAnimatorComponent(part)
                if partComponent is not None:
                    for func in args:
                        func(partComponent.visualGO, partComponent.animGO)

        return

    def turnOffRecorderHighlight(self):
        self.__recorderGO.removeComponentByType(SelectionComponent)

    def turnOnRecorderHighlight(self):
        if self.__recorderGO.findComponentByType(SelectionComponent) is None:
            self.__recorderGO.createComponent(SelectionComponent)
        return

    def turnOffHighlight(self):
        for _, gameObject in self.__pointsOfInterest:
            gameObject.removeComponentByType(SelectionComponent)

    def turnOnHighlight(self, activePoiCameraName):
        activePoiName = self.__cameraToPOI.get(activePoiCameraName, None)
        if activePoiName is None:
            return
        else:
            for _, gameObject in self.__pointsOfInterest:
                if gameObject.findComponentByType(SelectionComponent) is None:
                    poiComp = gameObject.findComponentByType(ArmoryPointOfInterest)
                    if poiComp is not None and poiComp.cameraName != activePoiName or poiComp is None:
                        gameObject.createComponent(SelectionComponent)

            return

    @cached_property
    def __hierarchyManager(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        return hierarchyManager
