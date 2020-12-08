# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/customizable_objects_manager.py
from collections import namedtuple
import BigWorld
import ResMgr
from helpers import dependency
from new_year.ny_constants import OBJECT_TO_ANCHOR, AnchorNames
from skeletons.new_year import ICustomizableObjectsManager, ICelebritySceneController
from helpers.EffectsList import effectsFromSection
from items.components.ny_constants import INVALID_TOY_ID
from items import collectibles
from slot_animation_service import SlotAnimationService
from .customization_camera import CustomizationCamera
_TOY_EFFECTS_CONFIG_FILE = 'scripts/new_year_effects.xml'
_CustomizableNodeDesc = namedtuple('CustomizableNodeDesc', ('isSelectable', 'modelName', 'outlineModelName', 'regularEffectName', 'hangingEffectName', 'animationSequence', 'hangingAnimationSequence', 'appearanceDelay'))

class CustomizableObjectsManager(ICustomizableObjectsManager):
    _celebrityController = dependency.descriptor(ICelebritySceneController)

    def __init__(self):
        super(CustomizableObjectsManager, self).__init__()
        self.__cameraAnchors = {}
        self.__cameraTargets = {}
        self.__customizableObjects = {}
        self.__pendingToys = {}
        self.__effectsCache = {}
        self.__currentObjectName = None
        self.__pendingEntitiesToDestroy = set()
        self.__slotsAnimation = None
        self.__cam = CustomizationCamera()
        self.__enities = set()
        return

    def init(self):
        self.__readEffects()
        self.__cam.init()

    def fini(self):
        self.__cam.destroy()
        self.__effectsCache.clear()
        self.__cameraAnchors.clear()
        self.__customizableObjects.clear()
        self.__pendingToys.clear()
        self.__pendingEntitiesToDestroy.clear()
        self.__enities = None
        if self.__slotsAnimation is not None:
            self.__slotsAnimation.fini()
            self.__slotsAnimation = None
        return

    @property
    def pendingEntitiesToDestroy(self):
        return self.__pendingEntitiesToDestroy

    def addCustomizableEntity(self, entity):
        anchorName = entity.anchorName
        self.__customizableObjects[anchorName] = entity
        pendingToys = self.__pendingToys.pop(anchorName, {})
        for node, slotInfo in pendingToys.iteritems():
            entity.updateNode(node, slotInfo)

        if self.__slotsAnimation is None:
            self.__slotsAnimation = SlotAnimationService()
        self.__slotsAnimation.addEntitySlots(entity)
        self.__enities.add(entity)
        return

    def removeCustomizableEntity(self, entity):
        self.__enities.discard(entity)
        if not self.__enities:
            if self.__slotsAnimation is not None:
                self.__slotsAnimation.fini()
            self.__slotsAnimation = None
        anchorName = entity.anchorName
        self.__pendingToys.pop(anchorName, None)
        self.__customizableObjects.pop(anchorName, None)
        return

    def getCustomizableEntity(self, anchorName):
        return None if anchorName not in self.__customizableObjects else self.__customizableObjects[anchorName]

    def addCameraAnchor(self, anchorName, anchor):
        self.__cameraAnchors[anchorName] = anchor

    def removeCameraAnchor(self, anchorName):
        if anchorName in self.__cameraAnchors:
            del self.__cameraAnchors[anchorName]

    def getCameraAnchor(self, anchorName):
        return None if anchorName not in self.__cameraAnchors else self.__cameraAnchors[anchorName]

    def addCameraTarget(self, anchorName, cameraTarget):
        self.__cameraTargets[anchorName] = cameraTarget

    def removeCameraTarget(self, anchorName):
        if anchorName in self.__cameraTargets:
            del self.__cameraTargets[anchorName]

    def getCameraTarget(self, anchorName):
        return self.__cameraTargets.get(anchorName)

    def updateSlot(self, slot, toy, withHangingEffect=True):
        nodes = slot.nodes.split()
        anchorName = OBJECT_TO_ANCHOR[slot.object]
        if toy is None or toy.id == INVALID_TOY_ID:
            if slot.defaultToy != INVALID_TOY_ID:
                toy = collectibles.g_cache.defaultToys.toys.get(slot.defaultToy)
        nodeDesc = None
        if toy is not None:
            toyModelName = getattr(toy, 'model', '')
            toyOutlineModelName = getattr(toy, 'outlineModel', '')
            toyRegularEffect = getattr(toy, 'regularEffect', '')
            toyHangingEffect = getattr(toy, 'hangingEffect', '') if withHangingEffect else ''
            if self.__isDeferredRenderPipeline():
                animationSeqAttr = 'animationSequence'
                hangingAnimationAttr = 'hangingAnimationSequence'
            else:
                animationSeqAttr = 'animationSequenceFwd'
                hangingAnimationAttr = 'hangingAnimationSequenceFwd'
            toyAnimationSequence = getattr(toy, animationSeqAttr, '')
            toyHangingAnimationSequence = getattr(toy, hangingAnimationAttr, '') if withHangingEffect else ''
            toyAppearanceDelay = getattr(toy, 'appearanceDelay', 0.0) if withHangingEffect else 0.0
            direction = slot.direction
            if not toyModelName and direction:
                directionModelAttr = ''.join(('model', '.', direction))
                toyModelName = getattr(toy, directionModelAttr, '')
            if not toyRegularEffect and direction:
                directionRegularEffectAttr = ''.join(('regularEffect', '.', direction))
                toyRegularEffect = getattr(toy, directionRegularEffectAttr, '')
            nodeDesc = _CustomizableNodeDesc(slot.selectable, toyModelName, toyOutlineModelName, toyRegularEffect, toyHangingEffect, toyAnimationSequence, toyHangingAnimationSequence, float(toyAppearanceDelay))
        for nodeName in nodes:
            if anchorName in self.__customizableObjects:
                self.__customizableObjects[anchorName].updateNode(nodeName, nodeDesc)
            self.__pendingToys.setdefault(anchorName, {})[nodeName] = nodeDesc

        return

    def getEffect(self, effectName):
        return self.__effectsCache.get(effectName)

    def switchCamera(self, anchorName):
        self.__cam.deactivate()
        if anchorName is not None:
            self.__switchToCameraAnchor(anchorName)
        return

    def setSlotHighlight(self, slot, isEnabled):
        if self.__slotsAnimation is not None:
            self.__slotsAnimation.changeState(slot, isEnabled)
        return

    def __switchToCameraAnchor(self, anchorName):
        if anchorName == AnchorNames.CELEBRITY and self._celebrityController.isChallengeCompleted:
            anchorName = AnchorNames.CELEBRITY_COMPLETED
        anchorDescr = self.getCameraAnchor(anchorName)
        if anchorDescr is not None:
            cameraTarget = self.getCameraTarget(anchorName)
            if cameraTarget is None:
                entity = self.getCustomizableEntity(anchorName)
                if entity is not None:
                    cameraTarget = entity.position
            if cameraTarget is not None:
                self.__cam.activate(cameraTarget, anchorDescr)
        return

    def __readEffects(self):
        effects = ResMgr.openSection(_TOY_EFFECTS_CONFIG_FILE) or {}
        for effect in effects.values():
            self.__effectsCache[effect.name] = effectsFromSection(effect)

        ResMgr.purge(_TOY_EFFECTS_CONFIG_FILE, True)

    @staticmethod
    def __isDeferredRenderPipeline():
        return BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 0
