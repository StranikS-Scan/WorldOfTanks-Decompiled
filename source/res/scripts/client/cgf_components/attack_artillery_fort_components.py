# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/attack_artillery_fort_components.py
from __future__ import absolute_import
import CGF
import GenericComponents
import Math
from GenericComponents import EntityGOSync
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CGF_DUMP, IS_CLIENT
from helpers import dependency
from helpers.gui_utils import hexARGBToRGBAFloatColor
if IS_CLIENT:
    from account_helpers.settings_core.settings_constants import GRAPHICS
    from skeletons.account_helpers.settings_core import ISettingsCore
else:

    class ISettingsCore(object):
        pass


@registerComponent
class ColorComponent(object):
    group = 'UI'
    editorTitle = 'Color Component'
    domain = CGF.Domain.ClientEditor
    model = ComponentProperty(type=CGF.PropertyType.Link, editorName='model', value=GenericComponents.DynamicModelComponent)
    colorParamName = ComponentProperty(type=CGF.PropertyType.String, editorName='colorParamName', value='g_color')
    color = ComponentProperty(type=CGF.PropertyType.Vector4, value=Math.Vector4(1, 0, 0, 0), editorName='color')

    def __init__(self):
        super(ColorComponent, self).__init__()
        self.currentColor = self.color
        self.currentColorParamName = self.colorParamName
        self.currentModel = self.model


class ColorSystem(CGF.System):
    ColorActivated = CGF.ActivateReaction(CGF.ReactRw(ColorComponent))
    ColorIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(ColorComponent))
    ModelAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.DynamicModelComponent))
    Reactions = CGF.Reactions(ColorActivated, ColorIterate, ModelAccess)

    def update(self):
        modelAccess = self.reaction(self.ModelAccess)
        for colorComponent in self.reaction(self.ColorActivated):
            self.handleColorComponentAdded(colorComponent, modelAccess)

        for colorComponent in self.reaction(self.ColorIterate):
            self.processingHandler(colorComponent, modelAccess)

    def handleColorComponentAdded(self, colorComponent, modelAccess):
        model = modelAccess.find(colorComponent.model)
        model.setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
        colorComponent.currentColor = colorComponent.color
        colorComponent.currentColorParamName = colorComponent.currentColorParamName
        colorComponent.currentModel = colorComponent.model

    def processingHandler(self, colorComponent, modelAccess):
        if colorComponent.currentColor != colorComponent.color or colorComponent.currentModel != colorComponent.model or colorComponent.currentColorParamName != colorComponent.colorParamName:
            model = modelAccess.find(colorComponent.model)
            model.setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
            colorComponent.currentColor = colorComponent.color
            colorComponent.currentColorParamName = colorComponent.colorParamName
            colorComponent.currentModel = colorComponent.model


@registerComponent
class ArtilleryFortColorComponent(object):
    group = 'Abilities'
    editorTitle = 'Artillery Fort Color'
    domain = CGF.Domain.ClientEditor
    colorComponent = ComponentProperty(type=CGF.PropertyType.Link, editorName='colorComponent', value=ColorComponent)

    def __init__(self):
        super(ArtilleryFortColorComponent, self).__init__()
        self.entityGO = None
        return


class AttackArtilleryFortColorSystem(CGF.System):
    if not IS_CGF_DUMP:
        __settingsCore = dependency.descriptor(ISettingsCore)
    FortColorActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(ArtilleryFortColorComponent))
    FortColorDeactivated = CGF.DeactivateReaction(CGF.ReactRw(ArtilleryFortColorComponent))
    FortColorIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(ArtilleryFortColorComponent))
    EntitySyncAccess = CGF.AccessReaction(CGF.Ro(EntityGOSync))
    ColorAccess = CGF.AccessReaction(CGF.Rw(ColorComponent))
    Reactions = CGF.Reactions(FortColorActivated, FortColorDeactivated, FortColorIterate, EntitySyncAccess, ColorAccess)

    def onMappingLoaded(self):
        if IS_CLIENT:
            self.__settingsCore.onSettingsChanged += self.colorSettingsChanged

    def onMappingUnloaded(self):
        if IS_CLIENT:
            self.__settingsCore.onSettingsChanged -= self.colorSettingsChanged

    def update(self):
        for fortColor in self.reaction(self.FortColorDeactivated):
            fortColor.entityGO = None

        entitySyncAccess = self.reaction(self.EntitySyncAccess)
        colorAccess = self.reaction(self.ColorAccess)
        for gameObject, fortColor in self.reaction(self.FortColorActivated):
            self.handleColorComponentAdded(gameObject, fortColor, entitySyncAccess, colorAccess)

        return

    def handleColorComponentAdded(self, gameObject, fortColor, entitySyncAccess, colorAccess):
        rootGameObject = self.hierarchy.getTopMostParent(gameObject)
        goSyncComponent = entitySyncAccess.find(rootGameObject)
        if goSyncComponent is not None:
            fortColor.entityGO = rootGameObject
            self.changeColor(fortColor, entitySyncAccess, colorAccess)
        return

    def colorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            entitySyncAccess = self.reaction(self.EntitySyncAccess)
            colorAccess = self.reaction(self.ColorAccess)
            for activeColor in self.reaction(self.FortColorIterate):
                self.changeColor(activeColor, entitySyncAccess, colorAccess)

    def changeColor(self, fortColor, entitySyncAccess, colorAccess):
        if fortColor.entityGO is not None and fortColor.entityGO.valid:
            goSyncComponent = entitySyncAccess.find(fortColor.entityGO)
            if goSyncComponent is not None:
                colorComponent = colorAccess.find(fortColor.colorComponent)
                colorComponent.color = hexARGBToRGBAFloatColor(goSyncComponent.entity.areaColor)
        return
