# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/customizable_objects_manager.py
import Event
import ResMgr
from skeletons.new_year import ICustomizableObjectsManager
from .abstract_switch_handler import AbstractSwitchHandler
from .mappings import AnchorNames
from PlayerEvents import g_playerEvents
from items.new_year_types import INVALID_TOY_ID
from collections import namedtuple
from helpers.EffectsList import effectsFromSection
from skeletons.new_year import INYSoundEvents
from helpers import dependency
_ENTITY_FOR_CHECK_LOADING = set(AnchorNames.ALL)
_TOY_EFFECTS_CONFIG_FILE = 'scripts/new_year_effects.xml'
_CustomizableNodeDesc = namedtuple('CustomizableNodeDesc', ('modelName', 'regularEffectName', 'hangingEffectName'))
_SlotInfo = namedtuple('_SlotInfo', ('slotType', 'nodeDesc'))

class CustomizableObjectsManager(AbstractSwitchHandler, ICustomizableObjectsManager):
    __DIRECTION_MASK = '%DIRECTION%'
    nySoundEvents = dependency.descriptor(INYSoundEvents)

    def __init__(self):
        super(CustomizableObjectsManager, self).__init__()
        self.onNYSceneObjectsLoadedEvent = Event.Event()
        self.__cameraAnchors = {}
        self.__customizableObjects = {}
        self.__selectableObjects = {}
        self.__pendingToys = {}
        self.__loadedEntityCount = 0
        self.__effectsCache = {}

    def init(self):
        g_playerEvents.onAccountShowGUI += self.__onAccountReady
        self.__loadedEntityCount = 0
        self.__readEffects()

    def fini(self):
        g_playerEvents.onAccountShowGUI -= self.__onAccountReady
        self.onNYSceneObjectsLoadedEvent.clear()
        self.__effectsCache.clear()
        self.__cameraAnchors.clear()
        self.__customizableObjects.clear()
        self.__selectableObjects.clear()
        self.__pendingToys.clear()
        super(CustomizableObjectsManager, self).fini()

    @property
    def state(self):
        return self._state

    @property
    def effectsCache(self):
        return self.__effectsCache

    def switchTo(self, state, callback=None):
        self.nySoundEvents.onCustomizationStateChanged(state)
        self._state = state
        super(CustomizableObjectsManager, self).switchTo(state, callback)

    def addCustomizableEntity(self, entity):
        anchorName = entity.anchorName
        self.__customizableObjects[anchorName] = entity
        entity.setEffectsCache(self.__effectsCache)
        pendingToys = self.__pendingToys.pop(anchorName, {})
        for node, slotInfo in pendingToys.iteritems():
            entity.updateNode(node, slotInfo)

        if self.__isEntityFilteredForLoading(entity):
            self.__loadedEntityCount += 1
            if self.__loadedEntityCount == len(_ENTITY_FOR_CHECK_LOADING):
                self.onNYSceneObjectsLoadedEvent()

    def removeCustomizableEntity(self, entity):
        anchorName = entity.anchorName
        self.__pendingToys.pop(anchorName, None)
        self.__customizableObjects.pop(anchorName, None)
        if self.__isEntityFilteredForLoading(entity):
            self.__loadedEntityCount -= 1
        return

    def enableAllSelectableEntities(self, isEnabled):
        for entity in self.__selectableObjects.values():
            entity.enable(isEnabled)

    def getCustomizableEntity(self, anchorName):
        return None if anchorName not in self.__customizableObjects else self.__customizableObjects[anchorName]

    def addSelectableEntity(self, entity):
        anchorName = entity.anchorName
        self.__selectableObjects[anchorName] = entity

    def removeSelectableEntity(self, entity):
        anchorName = entity.anchorName
        if anchorName in self.__selectableObjects:
            del self.__selectableObjects[anchorName]

    def addCameraAnchor(self, anchorName, anchor):
        self.__cameraAnchors[anchorName] = anchor

    def removeCameraAnchor(self, anchorName):
        if anchorName in self.__cameraAnchors:
            del self.__cameraAnchors[anchorName]

    def getCameraAnchor(self, anchorName):
        return None if anchorName not in self.__cameraAnchors else self.__cameraAnchors[anchorName]

    def updateSlot(self, slot, toy):
        nodes = slot.nodes.split()
        objectName = slot.object
        nodeDesc = None
        if toy.id != INVALID_TOY_ID:
            toyModelName = toy.model
            toyRegularEffect = toy.regularEffect
            direction = slot.direction
            if toyModelName and direction:
                toyModelName = toyModelName.replace(self.__DIRECTION_MASK, direction)
            if toyRegularEffect and direction:
                toyRegularEffect = toyRegularEffect.replace(self.__DIRECTION_MASK, direction)
            nodeDesc = _CustomizableNodeDesc(toyModelName, toyRegularEffect, toy.hangingEffect)
        slotInfo = _SlotInfo(slot.type, nodeDesc)
        for node in nodes:
            if objectName in self.__customizableObjects:
                self.__customizableObjects[objectName].updateNode(node, slotInfo)
            self.__pendingToys.setdefault(objectName, {})[node] = slotInfo

        return

    def __onAccountReady(self, _):
        self._resetState()

    def __readEffects(self):
        effects = ResMgr.openSection(_TOY_EFFECTS_CONFIG_FILE) or {}
        for effect in effects.values():
            self.__effectsCache[effect.name] = effectsFromSection(effect)

    @staticmethod
    def __isEntityFilteredForLoading(entity):
        return entity.anchorName in _ENTITY_FOR_CHECK_LOADING
