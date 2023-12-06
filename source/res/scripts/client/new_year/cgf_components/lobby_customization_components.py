# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/cgf_components/lobby_customization_components.py
import logging
import typing
import Math
import CGF
from collections import namedtuple
from GenericComponents import AnimatorComponent, HierarchyComponent, TransformComponent
from NyComponents import NySlotComponent
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from constants import IS_EDITOR
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import collectibles
from items.components.ny_constants import INVALID_TOY_ID
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
_CacheItem = namedtuple('CacheItem', ['gameObject', 'slotComponent', 'nodes'])

@registerComponent
class AppearanceDelayComponent(object):
    editorTitle = 'Appearance delay'
    category = 'New Year'
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0)


@registerComponent
class HangEffectsOwner(object):
    editorTitle = 'Hanging effect owner'
    category = 'New Year'


@registerComponent
class NyOutlineGoComponent(object):
    editorTitle = 'NY Outline Game object'
    category = 'New Year'


class LobbyCustomizableObjectsManager(CGF.ComponentManager):
    _nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(LobbyCustomizableObjectsManager, self).__init__()
        self.__hangEffectsEnabled = False
        self.__slotsCache = {}
        self.__callbacksCache = {}
        self.__installedToys = {}
        self.__callbackDelayer = CallbackDelayer()
        self.__highlightGameObjects = []

    def activate(self):
        self.__installedToys.clear()
        self._nyController.onUpdateSlot += self.updateSlot
        self._nyController.onSetHangToyEffectEnabled += self.setHangToyEffectEnabled
        if not IS_EDITOR and self.__hangarSpace.spaceInited:
            for slotID, toyID in enumerate(self.__itemsCache.items.festivity.getSlots()):
                self.updateSlot(slotID, toyID)

    def deactivate(self):
        self._nyController.onUpdateSlot -= self.updateSlot
        self._nyController.onSetHangToyEffectEnabled -= self.setHangToyEffectEnabled
        self.__slotsCache = {}
        self.__installedToys.clear()
        self.__clearToys()
        self.__callbackDelayer.clearCallbacks()
        self.__callbacksCache = {}
        for gameObject in self.__highlightGameObjects:
            CGF.removeGameObject(gameObject)

        self.__highlightGameObjects = []

    @onAddedQuery(NySlotComponent, CGF.GameObject)
    def onCustomizableSlotAdded(self, slotComponent, go):
        nodeGameObjects = self.__hierarchy.getChildren(go)
        nodes = []
        if nodeGameObjects:
            for nodeGameObject in nodeGameObjects:
                nodes.append(nodeGameObject)

        else:
            nodes.append(go)
        self.__slotsCache[slotComponent.id] = _CacheItem(go, slotComponent, nodes)
        if slotComponent.id in self.__installedToys:
            self.updateSlot(slotComponent.id, self.__installedToys[slotComponent.id])

    @onRemovedQuery(NySlotComponent, CGF.GameObject)
    def onCustomizableSlotRemoved(self, slotComponent, _):
        if self.__slotsCache.get(slotComponent.id):
            self.__slotsCache.pop(slotComponent.id)

    if not IS_EDITOR:

        @onAddedQuery(CGF.GameObject, AppearanceDelayComponent)
        def onAppearanceDelayAdded(self, go, delay):
            hierarchy = CGF.HierarchyManager(self.spaceID)
            children = hierarchy.getChildrenIncludingInactive(go)
            if not children:
                return
            for child in children:
                func = self.__callbacksCache[child.id] = child.activate
                self.__callbackDelayer.delayCallback(delay.delay, func)

        @onRemovedQuery(CGF.GameObject, AppearanceDelayComponent)
        def onAppearanceDelayRemoved(self, go, _):
            hierarchy = CGF.HierarchyManager(self.spaceID)
            children = hierarchy.getChildrenIncludingInactive(go)
            if not children:
                return
            for child in children:
                if child.id in self.__callbacksCache:
                    func = self.__callbacksCache.pop(child.id)
                    self.__callbackDelayer.stopCallback(func)

    @onAddedQuery(HangEffectsOwner, CGF.GameObject)
    def onHangEffectsOwnerAdded(self, hangEffectsOwner, go):
        if not self.__hangEffectsEnabled:
            return
        hierarchy = CGF.HierarchyManager(self.spaceID)
        children = hierarchy.getChildrenIncludingInactive(go)
        if not children:
            return
        for child in children:
            child.activate()

    @property
    def __hierarchy(self):
        return CGF.HierarchyManager(self.spaceID)

    def updateSlot(self, slotId, toyId):
        slotInfo = self.__slotsCache.get(slotId)
        self.__installedToys[slotId] = toyId
        if slotInfo is None:
            return
        else:
            if toyId == INVALID_TOY_ID:
                defaultToy = slotInfo.slotComponent.defaultToy
                if defaultToy is None or defaultToy == INVALID_TOY_ID:
                    self.__removeToys(slotId)
                    return
                toy = collectibles.g_cache.defaultToys.toys.get(defaultToy)
            else:
                toy = collectibles.g_cache.currentNyCollection.toys.get(toyId)
            if toy is None or not toy.hasPrefab():
                _logger.error('Could not find toy "%d" or toy prefab is not specified', toyId)
                return
            self.__removeToys(slotId)
            self.__loadToys(slotId, toy)
            return

    def updateSlotHighlight(self, slotId, isEnabled):
        slotInfo = self.__slotsCache.get(slotId)
        if slotInfo is None:
            _logger.info('Could not find slot "%d"', slotId)
            return
        elif not slotInfo.slotComponent.hoverEffect:
            return
        else:
            if isEnabled:
                nodes = slotInfo.nodes
                for node in nodes:
                    gameObject = CGF.GameObject(self.spaceID)
                    gameObject.createComponent(HierarchyComponent, node)
                    gameObject.createComponent(TransformComponent, Math.Vector3(0, 0, 0))
                    gameObject.createComponent(AnimatorComponent, slotInfo.slotComponent.hoverEffect, 0, 1, -1, True, '')
                    gameObject.activate()
                    self.__highlightGameObjects.append(gameObject)

            else:
                for gameObject in self.__highlightGameObjects:
                    CGF.removeGameObject(gameObject)

                self.__highlightGameObjects = []
            return

    def setHangToyEffectEnabled(self, enabled=True):
        self.__hangEffectsEnabled = enabled

    def __loadToys(self, slotId, toyDesc):
        for nodeGO in self.__slotsCache.get(slotId, _CacheItem(None, None, ())).nodes:
            CGF.loadGameObjectIntoHierarchy(toyDesc.prefab, nodeGO, Math.Vector3(0, 0, 0))

        return

    def __removeToys(self, slotId):
        for nodeGO in self.__slotsCache.get(slotId, _CacheItem(None, None, ())).nodes:
            toRemoveGOs = self.__hierarchy.getChildren(nodeGO)
            if toRemoveGOs:
                map(CGF.removeGameObject, toRemoveGOs)

        return

    def __clearToys(self):
        for slotId in self.__slotsCache.iterkeys():
            self.__removeToys(slotId)
