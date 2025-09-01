# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/color_blind_component.py
import typing
import CGF
import GenericComponents
from account_helpers.settings_core.settings_constants import GRAPHICS
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

def setModel(gameObject, isColorBlind, colorBlindComponent=None):
    colorBlindComponent = colorBlindComponent or gameObject.findComponentByType(ChangeModelOnColorBlindComponent)
    dynamicModelComponent = gameObject.findComponentByType(GenericComponents.DynamicModelComponent)
    if not colorBlindComponent or not colorBlindComponent.colorBlindModelPath or not dynamicModelComponent:
        return
    modelPath = colorBlindComponent.colorBlindModelPath if isColorBlind else colorBlindComponent.normalModel
    if dynamicModelComponent.getModelName() != modelPath:
        gameObject.removeComponent(dynamicModelComponent)
        gameObject.createComponent(GenericComponents.DynamicModelComponent, modelPath)


@registerComponent
class ChangeModelOnColorBlindComponent(object):
    category = 'Render'
    editorTitle = 'Change Model When Color Blind      [DEPRECATED]'
    domain = CGF.DomainOption.DomainClient
    colorBlindModelPath = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Color Blind Model Path', annotations={'path': '*.model'})

    def __init__(self):
        self.normalModel = None
        return


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ChangeModelOnColorBlindComponentManager(CGF.ComponentManager):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args):
        super(ChangeModelOnColorBlindComponentManager, self).__init__(*args)
        self._gameObjects = []

    @onAddedQuery(CGF.GameObject, ChangeModelOnColorBlindComponent)
    def onAdded(self, gameObject, component):
        dynamicModelComponent = gameObject.findComponentByType(GenericComponents.DynamicModelComponent)
        if dynamicModelComponent and component.normalModel is None:
            component.normalModel = dynamicModelComponent.getModelName()
        self._gameObjects.append(gameObject)
        setModel(gameObject, self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND), component)
        if len(self._gameObjects) == 1:
            self._settingsCore.onSettingsChanged += self._clientColorSettingsChanged
        return

    @onRemovedQuery(CGF.GameObject, ChangeModelOnColorBlindComponent)
    def onRemoved(self, gameObject, component):
        self._gameObjects.remove(gameObject)
        if not self._gameObjects:
            self._settingsCore.onSettingsChanged -= self._clientColorSettingsChanged

    def _clientColorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            isColorBlind = diff.get(GRAPHICS.COLOR_BLIND, False)
            for gameObject in self._gameObjects:
                setModel(gameObject, isColorBlind)
