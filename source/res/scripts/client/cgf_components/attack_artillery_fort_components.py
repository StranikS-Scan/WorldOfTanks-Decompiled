# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/attack_artillery_fort_components.py
import CGF
import GenericComponents
import Math
from GenericComponents import EntityGOSync
from cache import cached_property
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onProcessQuery, onRemovedQuery
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
    category = 'UI'
    editorTitle = 'Color Component'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    model = ComponentProperty(type=CGFMetaTypes.LINK, editorName='model', value=GenericComponents.DynamicModelComponent)
    colorParamName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='colorParamName', value='g_color')
    color = ComponentProperty(type=CGFMetaTypes.VECTOR4, value=Math.Vector4(1, 0, 0, 0), editorName='color')

    def __init__(self):
        super(ColorComponent, self).__init__()
        self.currentColor = self.color
        self.currentColorParamName = self.colorParamName
        self.currentModel = self.model


@autoregister(presentInAllWorlds=False, category='UI')
class ColorManager(CGF.ComponentManager):

    @onAddedQuery(ColorComponent)
    def handleColorComponentAdded(self, colorComponent):
        colorComponent.model().setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
        colorComponent.currentColor = colorComponent.color
        colorComponent.currentColorParamName = colorComponent.currentColorParamName
        colorComponent.currentModel = colorComponent.model

    @onProcessQuery(ColorComponent, tickGroup='Simulation')
    def processingHandler(self, colorComponent):
        if colorComponent.currentColor != colorComponent.color or colorComponent.currentModel != colorComponent.model or colorComponent.currentColorParamName != colorComponent.colorParamName:
            colorComponent.model().setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
            colorComponent.currentColor = colorComponent.color
            colorComponent.currentColorParamName = colorComponent.currentColorParamName
            colorComponent.currentModel = colorComponent.model


@registerComponent
class ArtilleryFortColorComponent(object):
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    colorComponent = ComponentProperty(type=CGFMetaTypes.LINK, editorName='colorComponent', value=ColorComponent)

    def __init__(self):
        super(ArtilleryFortColorComponent, self).__init__()
        self.entityGO = None
        return

    def changeColor(self):
        if self.entityGO is not None and self.entityGO.isValid():
            goSyncComponent = self.entityGO.findComponentByType(EntityGOSync)
            if goSyncComponent is not None:
                self.colorComponent().color = hexARGBToRGBAFloatColor(goSyncComponent.entity.areaColor)
        return

    def colorSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self.changeColor()


@autoregister(presentInAllWorlds=False, category='Abilities')
class AttackArtilleryFortColorManager(CGF.ComponentManager):
    if not IS_CGF_DUMP:
        __settingsCore = dependency.descriptor(ISettingsCore)

    @onAddedQuery(CGF.GameObject, ArtilleryFortColorComponent)
    def handleColorComponentAdded(self, gameObject, colorComponent):
        rootGameObject = self.__hierarchyManager.getTopMostParent(gameObject)
        goSyncComponent = rootGameObject.findComponentByType(EntityGOSync)
        if goSyncComponent is not None:
            colorComponent.entityGO = rootGameObject
            colorComponent.changeColor()
            if IS_CLIENT:
                self.__settingsCore.onSettingsChanged += colorComponent.colorSettingsChanged
        return

    @onRemovedQuery(ArtilleryFortColorComponent)
    def handleColorComponentRemoved(self, colorComponent):
        if colorComponent.entityGO is not None:
            if IS_CLIENT:
                self.__settingsCore.onSettingsChanged -= colorComponent.colorSettingsChanged
            colorComponent.entityGO = None
        return

    @cached_property
    def __hierarchyManager(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        return hierarchyManager
