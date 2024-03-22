# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/visual_effect_component_manager.py
import BigWorld
import CGF
import GenericComponents
import Triggers
from VehicleEffects import DamageFromShotDecoder
from account_helpers.settings_core.settings_constants import CONTOUR
from cgf_components.highlight_component import HighlightComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, Rule, registerManager, registerRule
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


class KillCamVisualEffectComponentManager(CGF.ComponentManager):
    __settingsCore = dependency.descriptor(ISettingsCore)

    @onAddedQuery(CGF.GameObject, HighlightComponent, Triggers.TimeTriggerComponent)
    def onCompoundModelAdded(self, go, highlightComponent, trigger):
        highlightComponent.callbackID = trigger.addFireReaction(self.__triggerReaction)

    @onRemovedQuery(HighlightComponent, Triggers.TimeTriggerComponent, GenericComponents.DynamicModelComponent)
    def onCompoundModelRemoved(self, highlightComponent, triggerComp, dynamicModelComponent):
        if highlightComponent.callbackID is not None:
            triggerComp.removeFireReaction(highlightComponent.callbackID)
        BigWorld.wgDelEdgeDetectDynamicModel(dynamicModelComponent)
        penZone = self.__settingsCore.getSetting(CONTOUR.CONTOUR_PENETRABLE_ZONE)
        nonPenZone = self.__settingsCore.getSetting(CONTOUR.CONTOUR_IMPENETRABLE_ZONE)
        BigWorld.setEdgeDrawerPenetratableZoneOverlay(penZone)
        BigWorld.setEdgeDrawerImpenetratableZoneOverlay(nonPenZone)
        return

    @onAddedQuery(CGF.GameObject, ImpactZoneComponent)
    def onDecalComponentAdded(self, go, decalComponent):
        for segment in decalComponent.segments:
            x = list(DamageFromShotDecoder.decodeSegment(segment, decalComponent.vehicleAppearance.collisions, decalComponent.maxComponentId))
            x[1] = vehicles.g_cache.damageStickers['ids'][decalComponent.modelName]
            if x[0] == TankPartIndexes.CHASSIS:
                go.removeComponent(ImpactZoneComponent)
                return
            decalComponent.vehicleAppearance.addDamageSticker(segment, x[0], x[1], x[2], x[3], 0.5)

    @staticmethod
    def __triggerReaction(go):
        dynMod = go.findComponentByType(GenericComponents.DynamicModelComponent)
        highlightComponent = go.findComponentByType(HighlightComponent)
        BigWorld.setEdgeDrawerImpenetratableZoneOverlay(0)
        BigWorld.setEdgeDrawerPenetratableZoneOverlay(0)
        BigWorld.wgAddEdgeDetectDynamicModel(dynMod, highlightComponent.colorIndex, highlightComponent.drawerMode)


@registerRule
class KillCamVisualEffectComponentManagerRule(Rule):
    category = 'KillCam Rule'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    @registerManager(KillCamVisualEffectComponentManager)
    def registerKillCamVisualEffectComponentManager(self):
        return None
