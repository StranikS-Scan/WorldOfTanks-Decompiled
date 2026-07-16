# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/visual_effect_component_manager.py
from __future__ import absolute_import
import BigWorld
import CGF
import GenericComponents
import Triggers
from VehicleEffects import DamageFromShotDecoder
from account_helpers.settings_core.settings_constants import CONTOUR
from cgf_components.highlight_component import HighlightComponent
from helpers import dependency
from items import vehicles
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartIndexes

class ImpactZoneComponent(object):

    def __init__(self, segments, vehicleAppearance, maxComponentId):
        super(ImpactZoneComponent, self).__init__()
        self.segments = segments
        self.vehicleAppearance = vehicleAppearance
        self.maxComponentId = maxComponentId
        self.modelName = 'impact_zone'


class KillCamVisualEffectComponentSystem(CGF.System):
    __settingsCore = dependency.descriptor(ISettingsCore)
    HighlightActivated = CGF.ActivateReaction(CGF.ReactRw(HighlightComponent), CGF.Rw(Triggers.TimeTriggerComponent))
    HighlightDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(HighlightComponent), CGF.Rw(Triggers.TimeTriggerComponent), GenericComponents.DynamicModelComponent)
    ModelAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.DynamicModelComponent), CGF.Rw(HighlightComponent))
    ImpactZoneActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(ImpactZoneComponent))
    Reactions = CGF.Reactions(HighlightActivated, HighlightDeactivated, ImpactZoneActivated, ModelAccess)

    def update(self):
        for _, highlight, trigger, model in self.reaction(self.HighlightDeactivated):
            if highlight.callbackID is not None:
                trigger.removeFireReaction(highlight.callbackID)
            BigWorld.wgDelEdgeDetectDynamicModel(model)
            penZone = self.__settingsCore.getSetting(CONTOUR.CONTOUR_PENETRABLE_ZONE)
            nonPenZone = self.__settingsCore.getSetting(CONTOUR.CONTOUR_IMPENETRABLE_ZONE)
            BigWorld.setEdgeDrawerPenetratableZoneOverlay(penZone)
            BigWorld.setEdgeDrawerImpenetratableZoneOverlay(nonPenZone)

        for highlight, trigger in self.reaction(self.HighlightActivated):
            highlight.callbackID = trigger.addFireReaction(self.__triggerReaction)

        for go, impact in self.reaction(self.ImpactZoneActivated):
            for segment in impact.segments:
                parsedData = DamageFromShotDecoder.parseDamageStickerHitPoint(segment, impact.vehicleAppearance.collisions, segLength=0.5)
                if parsedData is None:
                    continue
                stickerID, data = parsedData
                stickerID = vehicles.g_cache.damageStickers['ids'][impact.modelName]
                if data.componentIdx == TankPartIndexes.CHASSIS:
                    go.removeComponent(ImpactZoneComponent)
                    continue
                impact.vehicleAppearance.addDamageSticker(segment, stickerID, data)

        return

    def __triggerReaction(self, go):
        access = self.reaction(self.ModelAccess)
        dynMod, highlightComponent = access.find(go)
        if dynMod is None or highlightComponent is None:
            return
        else:
            BigWorld.setEdgeDrawerImpenetratableZoneOverlay(0)
            BigWorld.setEdgeDrawerPenetratableZoneOverlay(0)
            BigWorld.wgAddEdgeDetectDynamicModel(dynMod, highlightComponent.colorIndex, highlightComponent.drawerMode)
            return
