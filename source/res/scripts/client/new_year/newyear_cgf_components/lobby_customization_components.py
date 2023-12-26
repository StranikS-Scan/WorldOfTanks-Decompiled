# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/newyear_cgf_components/lobby_customization_components.py
import logging
import typing
from collections import namedtuple
import BigWorld
import Math
import CGF
from GenericComponents import AnimatorComponent
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from constants import IS_EDITOR
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import collectibles, new_year
from items.components.ny_constants import INVALID_TOY_ID
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)
_CacheItem = namedtuple('CacheItem', ['gameObject', 'slotComponent', 'nodes'])

@registerComponent
class NySlotComponent(object):
    editorTitle = 'Customization Slot'
    category = 'New Year'
    id = ComponentProperty(type=CGFMetaTypes.INT, editorName='ID', value=-1)
    toyType = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Toy type', value='')
    hoverEffect = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Hover effect', value='', annotations={'path': '*.seq'})
    defaultToy = ComponentProperty(type=CGFMetaTypes.INT, editorName='Default Toy', value=-1)


@registerComponent
class NyToyInfoHandlerComponent(object):
    editorTitle = 'Toy Info Handler'
    category = 'New Year'
    type = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Type', value='')
    showHighlight = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Show highlight', value=True)


@registerComponent
class NyToyInfoComponent(object):
    editorTitle = 'Toy Info'
    category = 'New Year'
    type = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Type', value='')


@registerComponent
class AppearanceDelayComponent(object):
    editorTitle = 'Appearance delay'
    category = 'New Year'
    delay = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Delay', value=0, annotations={'minMax': Math.Vector2(0, 10)})


@registerComponent
class HangEffectsOwner(object):
    editorTitle = 'Hanging effect owner'
    category = 'New Year'


class GraphicsPreference(object):
    DEFERRED = 'Deferred'
    FORWARD = 'Forward'
    ALL = (DEFERRED, FORWARD)


@registerComponent
class GraphicsPreferenceComponent(object):
    editorTitle = 'Graphics preference'
    category = 'New Year'
    graphicsPreset = ComponentProperty(type=CGFMetaTypes.STRING, value=GraphicsPreference.DEFERRED, annotations={'comboBox': {GraphicsPreference.DEFERRED: GraphicsPreference.DEFERRED,
                  GraphicsPreference.FORWARD: GraphicsPreference.FORWARD}})


@registerComponent
class NewYearTagComponent(object):
    editorTitle = 'NY Tag'
    category = 'New Year'
    tag = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Tag', value='')


@autoregister(presentInAllWorlds=False, category='New year rules')
class LobbyCustomizableObjectsManager(CGF.ComponentManager):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(LobbyCustomizableObjectsManager, self).__init__()
        self.__slotsCache = {}
        self.__callbacksCache = {}
        self.__installedToys = {}
        self.__callbackDelayer = CallbackDelayer()
        self.__highlightGameObjects = []

    def activate(self):
        self.__installedToys.clear()
        self._nyController.setHangToyEffectEnabled(False)
        self._nyController.onUpdateSlot += self.updateSlot

    def deactivate(self):
        self._nyController.onUpdateSlot -= self.updateSlot
        self.__slotsCache = {}
        self.__installedToys.clear()
        self.__clearToys()
        self.__callbackDelayer.clearCallbacks()
        self.__callbacksCache = {}
        for gameObject in self.__highlightGameObjects:
            gameObject.removeComponentByType(AnimatorComponent)

        self.__highlightGameObjects = []

    @onAddedQuery(NySlotComponent, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onCustomizableSlotAdded(self, slotComponent, go):
        nodeGameObjects = self.__hierarchy.getChildren(go)
        nodes = []
        if nodeGameObjects:
            for nodeGameObject in nodeGameObjects:
                nodes.append(nodeGameObject)

        else:
            nodes.append(go)
        self.__slotsCache[slotComponent.id] = _CacheItem(go, slotComponent, nodes)
        self.updateSlot(slotComponent.id, self._nyController.getInstalledToyInSlot(slotComponent.id))

    @onRemovedQuery(NySlotComponent, CGF.GameObject)
    def onCustomizableSlotRemoved(self, slotComponent, go):
        if self.__slotsCache.get(slotComponent.id):
            self.__slotsCache.pop(slotComponent.id)

    if not IS_EDITOR:

        @onAddedQuery(CGF.GameObject, AppearanceDelayComponent, tickGroup='postHierarchyUpdate')
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

    @onAddedQuery(HangEffectsOwner, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onHangEffectsOwnerAdded(self, hangEffectsOwner, go):
        if not self._nyController.getHangToyEffectEnabled():
            return
        hierarchy = CGF.HierarchyManager(self.spaceID)
        children = hierarchy.getChildrenIncludingInactive(go)
        if not children:
            return
        for child in children:
            child.activate()

    @onAddedQuery(CGF.GameObject, GraphicsPreferenceComponent, tickGroup='postHierarchyUpdate')
    def onGraphicsPreferenceAdded(self, go, graphicsPreference):
        graphicsPreset = GraphicsPreference.ALL.index(graphicsPreference.graphicsPreset)
        func = lambda node: node.deactivate()
        if graphicsPreset == BigWorld.getGraphicsSetting('RENDER_PIPELINE'):
            func = lambda node: node.activate()
        hierarchy = CGF.HierarchyManager(self.spaceID)
        children = hierarchy.getChildrenIncludingInactive(go)
        if not children:
            return
        for child in children:
            func(child)

    @onAddedQuery(NyToyInfoComponent, CGF.GameObject, tickGroup='postHierarchyUpdate')
    def onToyInfoAdded(self, toyInfo, go):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        parentGO = hierarchy.getParent(go)
        while parentGO.findComponentByType(NyToyInfoHandlerComponent) is None:
            parentGO = hierarchy.getParent(parentGO)
            if not parentGO.isValid():
                return

        handlerComponent = parentGO.findComponentByType(NyToyInfoHandlerComponent)
        if handlerComponent.type == toyInfo.type:
            children = hierarchy.getChildrenIncludingInactive(go)
            if not children:
                return
            for child in children:
                child.activate()

        return

    @property
    def __hierarchy(self):
        return CGF.HierarchyManager(self.spaceID)

    def updateSlot(self, slotId, toyId):
        if slotId in self.__installedToys and self.__installedToys[slotId] == toyId:
            return
        else:
            slotInfo = self.__slotsCache.get(slotId)
            if slotInfo is None:
                return
            toy = None
            if toyId == INVALID_TOY_ID:
                defaultToy = slotInfo.slotComponent.defaultToy
                if defaultToy is not None and defaultToy != INVALID_TOY_ID:
                    toy = collectibles.g_cache.defaultToys.toys.get(defaultToy)
            else:
                toy = new_year.g_cache.toys.get(toyId)
            self.__removeToys(slotId)
            if toy is not None:
                self.__loadToys(slotId, toy)
            self.__installedToys[slotId] = toyId
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
                    infoHandler = node.findComponentByType(NyToyInfoHandlerComponent)
                    if infoHandler and not infoHandler.showHighlight:
                        continue
                    node.createComponent(AnimatorComponent, slotInfo.slotComponent.hoverEffect, 0, 1, -1, True, '')
                    self.__highlightGameObjects.append(node)

            else:
                for gameObject in self.__highlightGameObjects:
                    gameObject.removeComponentByType(AnimatorComponent)

                self.__highlightGameObjects = []
            return

    def __loadToys(self, slotId, toyDesc):
        if toyDesc is None or not toyDesc.hasPrefab():
            _logger.error('Could not find toy "%d" or toy prefab is not specified', toyDesc.id)
            return
        else:
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
