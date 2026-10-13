# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/attack_artillery_fort_components.py
from __future__ import absolute_import
import CGF
from EntitySync import EntityGOSync
from cgf_components.color_components import ColorComponent
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
