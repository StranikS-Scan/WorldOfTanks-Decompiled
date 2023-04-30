# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/armory_yard_components.py
import CGF
import GenericComponents
import Event
from cache import cached_property
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery

@registerComponent
class ArmoryYardCameraRulesComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Armory Yard Camera Rules'
    category = 'Common'
    fromStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='From stage', value=0)
    toStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To stage', value=0)


@registerComponent
class AssemblyStageVideo(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Assembly stage video'
    category = 'Common'
    videoName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Video name')


@registerComponent
class TankAssemblyPartComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Tank Assembly Part'
    category = 'Common'
    index = ComponentProperty(type=CGFMetaTypes.INT, editorName='Group index', value=1)
    visualGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Visual part', value=CGF.GameObject)
    animGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Animation part', value=CGF.GameObject)


@registerComponent
class AssemblyStageIndex(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Assembly Stage Index'
    category = 'Common'
    index = ComponentProperty(type=CGFMetaTypes.INT, editorName='Stage index')


@registerComponent
class TankAssemblyRootComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Tank Assembly Root'
    category = 'Common'


@registerComponent
class SpawnProgressionComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Spawn progression'
    category = 'Common'
    progression = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='value', value=0.0)


@registerComponent
class HideDetailsAfterStageComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hide details after stage'
    category = 'Common'
    toHideAfterStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To hide after stage')


@registerComponent
class HideDetailsOnStageComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hide details on stage'
    category = 'Common'
    toHideOnStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To hide on stage')


@registerComponent
class SchemeStagesRuleComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Scheme stages rule'
    category = 'Common'
    fromStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='From stage')
    toStage = ComponentProperty(type=CGFMetaTypes.INT, editorName='To stage')


@registerComponent
class DetailsShadowManipulatorComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Details shadow manipulator'
    category = 'Common'
    enable = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Casts shadows', value=True)


@registerComponent
class RecorderComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Recorder component'
    category = 'Common'
    spool1 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Spool 1', value=CGF.GameObject)
    spool2 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Spool 2', value=CGF.GameObject)
    lamp = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Lamp', value=CGF.GameObject)
    lampAnimation = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Lamp animation', value=CGF.GameObject)


@registerComponent
class HangarDetailsComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hangar Details'
    category = 'Common'
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Prefab path', value='')


def partAnimatorComponent(part):
    partComponent = part.findComponentByType(TankAssemblyPartComponent)
    return (partComponent, partComponent.animGO.findComponentByType(GenericComponents.AnimatorComponent)) if partComponent is not None else (None, None)


@autoregister(presentInAllWorlds=True, category='UI')
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
        self.__stageCameraGOs = []
        self.__hangarDetailsGO = None
        self.__hangarDetailsPath = ''
        self.__hangarDetailsPos = None
        self.__recorderGO = None
        return

    @onRemovedQuery(TankAssemblyRootComponent, CGF.GameObject)
    def onRemoved(self, rootComponent, gameObject):
        self.__stageIndexToStageGO = {}
        self.__stageGroupParts = {}
        self.__stageGroupDuration = {}
        self.__stageVideo = {}
        self.__toHideListAfterStageGO = []
        self.__toHideListOnStageGO = []
        self.__stageCameraGOs = []
        self.__rootObject = None
        self.__hangarDetailsGO = None
        self.__hangarDetailsPath = ''
        self.__hangarDetailsPos = None
        self.__recorderGO = None
        self.__eventManager.clear()
        return

    @onAddedQuery(HideDetailsAfterStageComponent, CGF.GameObject)
    def onAddedHideDetailsAfterStageComponent(self, hideComponent, gameObject):
        self.__toHideListAfterStageGO.append((hideComponent.toHideAfterStage, gameObject))

    @onAddedQuery(HideDetailsOnStageComponent, CGF.GameObject)
    def onAddedHideDetailsOnStageComponent(self, hideComponent, gameObject):
        self.__toHideListOnStageGO.append((hideComponent.toHideOnStage, gameObject))

    @onAddedQuery(SpawnProgressionComponent, CGF.GameObject)
    def onAddedSpawnProgression(self, spawnProgressionComponent, gameObject):
        dynamicModelComponent = gameObject.findComponentByType(GenericComponents.DynamicModelComponent)
        if dynamicModelComponent is not None:
            dynamicModelComponent.setMaterialParameterFloat('spawnProgeression', spawnProgressionComponent.progression)
        return

    @onAddedQuery(GenericComponents.DynamicModelComponent, DetailsShadowManipulatorComponent)
    def onAddedModelWithShadowManipulator(self, dynamicModelComponent, shadowComponent):
        dynamicModelComponent.setCastsShadows(shadowComponent.enable)

    @onAddedQuery(ArmoryYardCameraRulesComponent, CGF.GameObject)
    def onAddedCameraRule(self, cameraRulesComponent, go):
        self.__stageCameraGOs.append(((cameraRulesComponent.fromStage, cameraRulesComponent.toStage), go))

    @onAddedQuery(RecorderComponent, GenericComponents.VSEComponent, CGF.GameObject)
    def onAddedRecorder(self, recorderComp, vseComponent, gameObject):
        self.__recorderGO = gameObject

    @onAddedQuery(HangarDetailsComponent, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onAddedHangarDetails(self, detailsComponent, gameObject):
        self.__hangarDetailsGO = gameObject
        self.__hangarDetailsPath = detailsComponent.prefabPath
        transformComponent = gameObject.findComponentByType(GenericComponents.TransformComponent)
        self.__hangarDetailsPos = transformComponent.worldTransform

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

    def activateStageGroup(self, stageIndex, stageGroupId):
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

    def endStageGroup(self, stageIndex, stageGroupId):
        self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: visualGO.activate(), lambda visualGO, animGO: animGO.deactivate())

    def deactivateStageGroup(self, stageIndex, stageGroupId):
        self.__stageActivation(stageIndex, stageGroupId, lambda visualGO, animGO: visualGO.deactivate(), lambda visualGO, animGO: animGO.deactivate())

    def deactivateAllStage(self):
        for stageIndex in self.__stageIndexToStageGO:
            self.deactivateSingleStage(stageIndex)

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

    def getHangarDetailsPath(self):
        return self.__hangarDetailsPath

    def getHangarDetailsGameObject(self):
        return self.__hangarDetailsGO

    def getHangarDetailsPosition(self):
        return self.__hangarDetailsPos

    def getSchemeStagesRange(self):
        return self.__schemeStagesRange

    def getCameraDataByStageIndex(self, stageIndex):
        for (stageIndexFrom, stageIndexTo), gameObject in self.__stageCameraGOs:
            if stageIndexFrom <= stageIndex <= stageIndexTo:
                return gameObject

        return None

    def stageIsPlaying(self, stageIndex):
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

    @cached_property
    def __hierarchyManager(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        return hierarchyManager
