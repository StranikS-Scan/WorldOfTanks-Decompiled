# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/color_blind_component.py
from __future__ import absolute_import
import typing
import CGF
import GenericComponents
from account_helpers.settings_core.settings_constants import GRAPHICS
from cgf_script.registration import ComponentProperty, registerComponent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

def setModel(gameObject, isColorBlind, queue, dynamicModelPath, colorBlindComponent=None):
    if not colorBlindComponent or not colorBlindComponent.colorBlindModelPath:
        return
    modelPath = colorBlindComponent.colorBlindModelPath if isColorBlind else colorBlindComponent.normalModel
    if dynamicModelPath != modelPath:
        queue.removeComponent(gameObject, GenericComponents.DynamicModelComponent)
        queue.createComponent(gameObject, GenericComponents.DynamicModelComponent, modelPath)


@registerComponent
class ChangeModelOnColorBlindComponent(object):
    group = 'Render'
    editorTitle = 'Change Model When Color Blind      [DEPRECATED]'
    domain = CGF.Domain.Client
    colorBlindModelPath = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Color Blind Model Path', annotations={'path': '*.model'})

    def __init__(self):
        self.normalModel = None
        return


class ChangeModelOnColorBlindComponentSystem(CGF.System):
    _settingsCore = dependency.descriptor(ISettingsCore)
    ChangeModelActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(ChangeModelOnColorBlindComponent))
    ChangeModelDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(ChangeModelOnColorBlindComponent))
    ModelAccess = CGF.AccessReaction(CGF.Ro(GenericComponents.DynamicModelComponent))
    ChangeModelAccess = CGF.AccessReaction(CGF.Ro(ChangeModelOnColorBlindComponent))
    Reactions = CGF.Reactions(ChangeModelActivated, ChangeModelDeactivated, ModelAccess, ChangeModelAccess)

    def __init__(self, *args):
        super(ChangeModelOnColorBlindComponentSystem, self).__init__(*args)
        self._gameObjects = []

    def update(self):
        for gameObject, _ in self.reaction(self.ChangeModelDeactivated):
            self.onRemoved(gameObject)

        modelAccess = self.reaction(self.ModelAccess)
        for gameObject, component in self.reaction(self.ChangeModelActivated):
            self.onAdded(gameObject, component, modelAccess)

    def onAdded(self, gameObject, component, modelAccess):
        dynamicModelComponent = modelAccess.find(gameObject)
        if dynamicModelComponent and component.normalModel is None:
            component.normalModel = dynamicModelComponent.getModelName()
        self._gameObjects.append(gameObject)
        if dynamicModelComponent:
            q = CGF.CommandQueue(self.gom)
            setModel(gameObject, self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND), q, dynamicModelComponent.getModelName(), component)
        if len(self._gameObjects) == 1:
            self._settingsCore.onSettingsChanged += self._clientColorSettingsChanged
        return

    def onRemoved(self, gameObject):
        self._gameObjects.remove(gameObject)
        if not self._gameObjects:
            self._settingsCore.onSettingsChanged -= self._clientColorSettingsChanged

    def _clientColorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            isColorBlind = diff.get(GRAPHICS.COLOR_BLIND, False)
            changeModelAccess = self.reaction(self.ChangeModelAccess)
            modelAccess = self.reaction(self.ModelAccess)
            q = CGF.CommandQueue(self.gom)
            for gameObject in self._gameObjects:
                dynamicModelComponent = modelAccess.find(gameObject)
                if dynamicModelComponent:
                    setModel(gameObject, isColorBlind, q, dynamicModelComponent.getModelName(), changeModelAccess.find(gameObject))
