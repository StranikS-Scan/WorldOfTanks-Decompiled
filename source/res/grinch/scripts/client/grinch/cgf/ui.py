# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/cgf/ui.py
import weakref
import BigWorld
import CGF
import Math
import math_utils
import GenericComponents
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from grinch.cgf import getVehicleFromGO
from grinch_common.grinch_constants import ARENA_BONUS_TYPE_CAPS
from grinch_common.cgf.presents import HomebaseComponent
from constants import IS_CLIENT, NULL_ENTITY_ID
from helpers import dependency
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask, MinimapMarkerComponent
    from grinch.gui.shared.events import TurretDeployEvent, RageAbilityEvent, FlareAbilityEvent, HomebaseMarkerEvent
else:

    class AreaMarker(object):
        pass


    class MinimapMarkerComponent(object):
        pass


    class IBattleSessionProvider(object):
        pass


    class TurretDeployEvent(object):
        pass


    class RageAbilityEvent(object):
        pass


    class FlareAbilityEvent(object):
        pass


    class HomebaseMarkerEvent(object):
        pass


def getHomebaseMarkerTransform(team):
    spaceID = BigWorld.player().spaceID
    hierarchy = CGF.HierarchyManager(spaceID)
    query = CGF.Query(spaceID, (CGF.GameObject, HomebaseComponent))
    for homebaseGO, homebaseComp in query:
        if team == homebaseComp.team:
            for go, _ in hierarchy.findComponentsInHierarchy(homebaseGO, GrinchHomebaseMarker):
                tranformComponent = go.findComponentByType(GenericComponents.TransformComponent)
                if tranformComponent:
                    return tranformComponent.worldTransform

    return Math.Matrix()


class StaticMinimapMarkerComponent(MinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        config = self._config
        gui.invoke(self._componentID, 'as_setIcon', config['icon'])


class DynamicMinimapMarkerComponent(MinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        config = self._config
        gui.invoke(self._componentID, 'as_setIcon', config['icon'])


class StaticAreaMarker(AreaMarker):
    COMPONENT_CLASS = {2: StaticMinimapMarkerComponent}


class DynamicAreaMarker(AreaMarker):
    COMPONENT_CLASS = {2: DynamicMinimapMarkerComponent}


@registerComponent
class GrinchHomebaseMarker(object):
    category = 'Grinch'
    editorTitle = 'Grinch Homebase Marker'
    domain = CGF.DomainOption.DomainClient


@registerComponent
class GrinchDeployMarker(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainClient
    source = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='source')

    def __init__(self):
        super(GrinchDeployMarker, self).__init__()
        self.vehicleID = NULL_ENTITY_ID
        self.sourceComponent = None
        return


@registerComponent
class GrinchFlareMarker(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainClient

    def __init__(self):
        super(GrinchFlareMarker, self).__init__()
        self.vehicleID = NULL_ENTITY_ID


@registerComponent
class GrinchFlareVehicleStatusEffect(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainClient
    source = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='source')

    def __init__(self):
        super(GrinchFlareVehicleStatusEffect, self).__init__()
        self.vehicleID = NULL_ENTITY_ID
        self.sourceComponent = None
        self.currentEndTime = 0.0
        return


@registerComponent
class GrinchRageUndeadMarker(object):
    category = 'Grinch'
    editorTitle = 'Grinch Rage Undead Marker'
    domain = CGF.DomainOption.DomainClient

    def __init__(self):
        super(GrinchRageUndeadMarker, self).__init__()
        self.vehicleID = NULL_ENTITY_ID


@registerComponent
class GrinchMinimapMarker(object):
    category = 'Grinch'
    editorTitle = 'Grinch Minimap Marker'
    domain = CGF.DomainOption.DomainClient
    symbol = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Symbol')
    container = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Container')
    onlyTranslation = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Only Translation')
    offset = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(0, 0, 0), editorName='offset')
    areaRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.0, editorName='areaRadius')
    disappearanceRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=1.0, editorName='Disappearance Radius')
    reverseDisappearing = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Reverse disappearing')
    type = ComponentProperty(type=CGFMetaTypes.STRING, value='static', editorName='MarkerType')

    def __init__(self):
        super(GrinchMinimapMarker, self).__init__()
        self.marker = None
        self.markerID = None
        return


@registerComponent
class GrinchFreezedVehicleStatusEffect(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainClient
    source = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='source')

    def __init__(self):
        super(GrinchFreezedVehicleStatusEffect, self).__init__()
        self.vehicleID = NULL_ENTITY_ID
        self.sourceComponent = None
        self.currentEndTime = 0.0
        return


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudHomebaseMarkerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GrinchHomebaseMarker, GenericComponents.TransformComponent, tickGroup='postTickUpdate')
    def onAddedHomebaseMarker(self, go, _, transform):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        hierarchyManager = CGF.HierarchyManager(go.spaceID)
        if not hierarchyManager:
            return
        homebaseGO = hierarchyManager.getTopMostParent(go)
        homebase = homebaseGO.findComponentByType(HomebaseComponent)
        if not homebase:
            return
        g_eventBus.handleEvent(HomebaseMarkerEvent(HomebaseMarkerEvent.HOMEBASE_MARKER_UPDATE, team=homebase.team, matrix=transform.worldTransform), scope=EVENT_BUS_SCOPE.BATTLE)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudMinimapManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(GrinchMinimapMarker, GenericComponents.TransformComponent)
    def onAddedMinimapMarker(self, marker, transform):
        transform = transform.worldTransform
        matrixProduct = math_utils.MatrixProviders.product(transform, math_utils.createTranslationMatrix(marker.offset))
        data = {'visible': True,
         'areaRadius': marker.areaRadius,
         'disappearingRadius': marker.disappearanceRadius,
         'reverseDisappearing': marker.reverseDisappearing,
         ComponentBitMask.MINIMAP_MARKER: [{'symbol': 'DynamicEntry' if marker.type == 'dynamic' else 'StaticEntry',
                                            'icon': marker.symbol,
                                            'container': marker.container,
                                            'onlyTranslation': marker.onlyTranslation}],
         'matrixProduct': matrixProduct,
         'bitMask': ComponentBitMask.MINIMAP_MARKER}
        marker.marker = DynamicAreaMarker(data) if marker.type == 'dynamic' else StaticAreaMarker(data)
        marker.markerID = self.__guiSessionProvider.shared.areaMarker.addMarker(marker.marker)

    @onRemovedQuery(GrinchMinimapMarker)
    def onRemovedMinimapMarker(self, marker):
        areaMarkerCtrl = self.__guiSessionProvider.shared.areaMarker
        if areaMarkerCtrl:
            areaMarkerCtrl.removeMarker(marker.markerID)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudDeployMarkerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GrinchDeployMarker)
    def onAddedGrinchDeployMarker(self, go, marker):
        vehicle = getVehicleFromGO(self.spaceID, go)
        if vehicle and marker.source in vehicle.components:
            marker.vehicleID = vehicle.id
            marker.sourceComponent = weakref.proxy(vehicle.components.get(marker.source))

    @onRemovedQuery(GrinchDeployMarker)
    def onRemovedGrinchDeployMarker(self, marker):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(TurretDeployEvent(TurretDeployEvent.TURRET_DEPLOY_TIME_CHANGED, deployTimeLeft=0, vehicleID=marker.vehicleID), scope=EVENT_BUS_SCOPE.BATTLE)

    @onProcessQuery(GrinchDeployMarker, updatePeriod=0.1)
    def onProcessGrinchDeployMarker(self, marker):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        if not marker.vehicleID:
            return
        timeLeft = marker.sourceComponent.endtime - BigWorld.serverTime()
        g_eventBus.handleEvent(TurretDeployEvent(TurretDeployEvent.TURRET_DEPLOY_TIME_CHANGED, deployTimeLeft=timeLeft, vehicleID=marker.vehicleID), scope=EVENT_BUS_SCOPE.BATTLE)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudRageUndeadMarkerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GrinchRageUndeadMarker)
    def onAddedGrinchRageUndeadMarker(self, go, undeadMarker):
        vehicle = getVehicleFromGO(self.spaceID, go)
        if vehicle:
            undeadMarker.vehicleID = vehicle.id
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(RageAbilityEvent(RageAbilityEvent.VEHICLE_STATUS_CHANGED, vehicleUndeadStatus=True, vehicleID=undeadMarker.vehicleID), scope=EVENT_BUS_SCOPE.BATTLE)

    @onRemovedQuery(GrinchRageUndeadMarker)
    def onRemovedGrinchDeployMarker(self, undeadMarker):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(RageAbilityEvent(RageAbilityEvent.VEHICLE_STATUS_CHANGED, vehicleUndeadStatus=False, vehicleID=undeadMarker.vehicleID), scope=EVENT_BUS_SCOPE.BATTLE)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudFlareMarkerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GrinchFlareMarker)
    def onAddedGrinchFlareMarker(self, go, marker):
        vehicle = getVehicleFromGO(self.spaceID, go)
        if vehicle:
            marker.vehicleID = vehicle.id
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(FlareAbilityEvent(FlareAbilityEvent.FLARE_MARK, vehicleID=marker.vehicleID, isOn=True), scope=EVENT_BUS_SCOPE.BATTLE)

    @onRemovedQuery(GrinchFlareMarker)
    def onRemovedGrinchFlareMarker(self, marker):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(FlareAbilityEvent(FlareAbilityEvent.FLARE_MARK, vehicleID=marker.vehicleID, isOn=False), scope=EVENT_BUS_SCOPE.BATTLE)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudFlareVehicleStatusEffectManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    MARKED_BY_FLARE_VEHICLE_STATE = 'grinchMarkedByFlare'

    @onAddedQuery(CGF.GameObject, GrinchFlareVehicleStatusEffect)
    def onAddedGrinchFlareVehicleStatusEffect(self, go, marker):
        vehicle = getVehicleFromGO(self.spaceID, go)
        if not vehicle:
            return
        marker.vehicleID = vehicle.id
        marker.sourceComponent = weakref.proxy(vehicle.components.get(marker.source))

    @onRemovedQuery(GrinchFlareVehicleStatusEffect)
    def onRemovedGrinchFlareVehicleStatusEffect(self, marker):
        if not marker.vehicleID or marker.vehicleID != getattr(BigWorld.player(), 'playerVehicleID', 0):
            return
        else:
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.STEALTH_RADAR, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.STEALTH_RADAR, 0.0, None))
            return

    @onProcessQuery(CGF.GameObject, GrinchFlareVehicleStatusEffect, updatePeriod=0.1)
    def onProcessGrinchFlareVehicleStatusEffect(self, go, marker):
        if not marker.vehicleID:
            return
        playerAvatar = BigWorld.player()
        if not playerAvatar:
            return
        if marker.vehicleID != getattr(playerAvatar, 'playerVehicleID', 0):
            return
        if not playerAvatar.isVehicleAlive:
            if go.findComponentByType(GrinchFlareVehicleStatusEffect):
                go.removeComponentByType(GrinchFlareVehicleStatusEffect)
            return
        endtime = marker.sourceComponent.endtime
        if marker.currentEndTime != endtime:
            marker.currentEndTime = endtime
            startTime = BigWorld.serverTime()
            timeLeft = endtime - startTime
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.STEALTH_RADAR, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.STEALTH_RADAR, level=battle_constants.TIMER_VIEW_STATE.CRITICAL, startTime=startTime, totalTime=timeLeft))


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchHudFreezedVehicleStatusEffectManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(CGF.GameObject, GrinchFreezedVehicleStatusEffect)
    def onAddedGrinchFreezedVehicleStatusEffect(self, go, marker):
        vehicle = getVehicleFromGO(self.spaceID, go)
        if vehicle and marker.source in vehicle.components:
            marker.vehicleID = vehicle.id
            marker.sourceComponent = weakref.proxy(vehicle.components.get(marker.source))

    @onRemovedQuery(GrinchFreezedVehicleStatusEffect)
    def onRemovedGrinchFreezedVehicleStatusEffect(self, marker):
        if not marker.vehicleID or marker.vehicleID != getattr(BigWorld.player(), 'playerVehicleID', 0):
            return
        else:
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.DANGER_ZONE, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.DANGER_ZONE, 0.0, None))
            return

    @onProcessQuery(CGF.GameObject, GrinchFreezedVehicleStatusEffect, updatePeriod=0.1)
    def onProcessGrinchFreezedVehicleStatusEffect(self, go, marker):
        if not marker.vehicleID:
            return
        playerAvatar = BigWorld.player()
        if not playerAvatar:
            return
        if marker.vehicleID != getattr(playerAvatar, 'playerVehicleID', 0):
            return
        if not playerAvatar.isVehicleAlive:
            if go.findComponentByType(GrinchFreezedVehicleStatusEffect):
                go.removeComponentByType(GrinchFreezedVehicleStatusEffect)
            return
        endtime = marker.sourceComponent.endtime
        if marker.currentEndTime != endtime:
            marker.currentEndTime = endtime
            startTime = BigWorld.serverTime()
            timeLeft = endtime - startTime
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.DANGER_ZONE, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.DANGER_ZONE, level=battle_constants.TIMER_VIEW_STATE.CRITICAL, startTime=startTime, totalTime=timeLeft))
