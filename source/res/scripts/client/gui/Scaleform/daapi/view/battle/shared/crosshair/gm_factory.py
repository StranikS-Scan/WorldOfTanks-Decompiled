# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/gm_factory.py
from typing import Type
import BattleReplay
from AvatarInputHandler.gun_marker_ctrl import useDefaultGunMarkers
from aih_constants import GUN_MARKER_TYPE
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import DefaultGunMarkerComponent
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import GunMarkerComponent
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import GunMarkersComponents
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import SPGGunMarkerComponent
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import VideoGunMarkerComponent
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _CONSTANTS
from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID as _VIEW_ID
from gui.battle_control.controllers.crosshair_proxy import GunMarkersSetInfo
_GUN_MARKER_LINKAGES = {_CONSTANTS.ARCADE_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_LINKAGE,
 _CONSTANTS.SNIPER_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_LINKAGE,
 _CONSTANTS.SPG_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_SPG_LINKAGE,
 _CONSTANTS.DUAL_GUN_ARCADE_MARKER_NAME: _CONSTANTS.DUAL_GUN_ARCADE_MARKER_LINKAGE,
 _CONSTANTS.DUAL_GUN_SNIPER_MARKER_NAME: _CONSTANTS.DUAL_GUN_SNIPER_MARKER_LINKAGE,
 _CONSTANTS.ARCADE_DUAL_ACC_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_LINKAGE,
 _CONSTANTS.SNIPER_DUAL_ACC_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_LINKAGE,
 _CONSTANTS.DEBUG_ARCADE_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_DEBUG_LINKAGE,
 _CONSTANTS.DEBUG_SNIPER_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_DEBUG_LINKAGE,
 _CONSTANTS.DEBUG_SPG_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_SPG_DEBUG_LINKAGE,
 _CONSTANTS.DEBUG_DUAL_GUN_ARCADE_MARKER_NAME: _CONSTANTS.DUAL_GUN_ARCADE_MARKER_DEBUG_LINKAGE,
 _CONSTANTS.DEBUG_DUAL_GUN_SNIPER_MARKER_NAME: _CONSTANTS.DUAL_GUN_SNIPER_MARKER_DEBUG_LINKAGE,
 _CONSTANTS.ARTY_HIT_MARKER_NAME: _CONSTANTS.ARTY_HIT_MARKER_LINKAGE,
 _CONSTANTS.VIDEO_GUN_MARKER_NAME: _CONSTANTS.GUN_MARKER_LINKAGE}

class _GunMarkersFactories(object):

    def __init__(self, *factories):
        super(_GunMarkersFactories, self).__init__()
        self.__factories = factories

    def create(self, markersInfo, vehicleInfo):
        return self._create(markersInfo, vehicleInfo, components=None)

    def override(self, components, markersInfo, vehicleInfo):
        return self._create(markersInfo, vehicleInfo, components=components)

    def _create(self, markersInfo, vehicleInfo, components=None):
        markers = ()
        for factory in self.__factories:
            result = factory(markersInfo, vehicleInfo, components).create()
            if result:
                markers = markers + result

        return GunMarkersComponents(markers)


class _GunMarkersFactory(object):
    __slots__ = ('_components', '_markersInfo', '_vehicleInfo')

    def __init__(self, markersInfo, vehicleInfo, components=None):
        super(_GunMarkersFactory, self).__init__()
        self._components = components
        self._markersInfo = markersInfo
        self._vehicleInfo = vehicleInfo

    def create(self):
        raise NotImplementedError

    def _findMarker(self, name):
        marker = None
        if self._components is not None:
            marker = self._components.popComponent(name)
        return marker

    def _createMarker(self, componentClass, viewId, markerType, dataProvider, name, isActive=False):
        marker = self._findMarker(name)
        if marker is not None:
            marker.setDataProvider(markerType, dataProvider)
            return marker
        else:
            linkage = _GUN_MARKER_LINKAGES[name]
            return componentClass(markerType, viewId, name, linkage, dataProvider, isActive)

    def _getMarkerDataProvider(self, markerType):
        if markerType is GUN_MARKER_TYPE.SERVER:
            return self._markersInfo.serverMarkerDataProvider
        elif markerType is GUN_MARKER_TYPE.CLIENT:
            return self._markersInfo.clientMarkerDataProvider
        else:
            return self._markersInfo.dualAccMarkerDataProvider if markerType is GUN_MARKER_TYPE.DUAL_ACC else None

    def _getSPGDataProvider(self, markerType):
        if markerType is GUN_MARKER_TYPE.SERVER:
            return self._markersInfo.serverSPGMarkerDataProvider
        else:
            return self._markersInfo.clientSPGMarkerDataProvider if markerType is GUN_MARKER_TYPE.CLIENT else None


class _ControlMarkersFactory(_GunMarkersFactory):

    def create(self):
        if self._vehicleInfo.isSPG():
            markers = self._createSPGMarkers()
        elif self._vehicleInfo.isDualGunVehicle():
            markers = self._createDualGunMarkers()
        elif self._hasDualAccuracyMarkers():
            markers = self._createDualAccMarkers()
        elif self._vehicleInfo.isFlamethrowerVehicle():
            markers = self._createFlamethrowerMarkers()
        else:
            markers = self._createDefaultMarkers()
        return markers

    def _hasDualAccuracyMarkers(self):
        isClientMarkers = self._getMarkerType() == GUN_MARKER_TYPE.CLIENT
        isClientMarkers = isClientMarkers and not BattleReplay.g_replayCtrl.isServerAim
        return isClientMarkers and self._vehicleInfo.isPlayerVehicle() and self._vehicleInfo.hasDualAccuracy()

    def _getMarkerType(self):
        if self._markersInfo.isServerMarkerActivated:
            return GUN_MARKER_TYPE.SERVER
        return GUN_MARKER_TYPE.CLIENT if self._markersInfo.isClientMarkerActivated else GUN_MARKER_TYPE.UNDEFINED

    def _createDualGunMarkers(self):
        markerType = self._getMarkerType()
        return (self._createArcadeMarker(markerType, _CONSTANTS.DUAL_GUN_ARCADE_MARKER_NAME), self._createSniperMarker(markerType, _CONSTANTS.DUAL_GUN_SNIPER_MARKER_NAME))

    def _createDualAccMarkers(self):
        return self._createDefaultMarkers() + (self._createArcadeMarker(GUN_MARKER_TYPE.DUAL_ACC, _CONSTANTS.ARCADE_DUAL_ACC_GUN_MARKER_NAME), self._createSniperMarker(GUN_MARKER_TYPE.DUAL_ACC, _CONSTANTS.SNIPER_DUAL_ACC_GUN_MARKER_NAME))

    def _createFlamethrowerMarkers(self):
        markerType = self._getMarkerType()
        return (self._createArcadeMarker(markerType, name=_CONSTANTS.ARCADE_GUN_MARKER_NAME), self._createSPGMarker(markerType, name=_CONSTANTS.SPG_GUN_MARKER_NAME))

    def _createDefaultMarkers(self):
        markerType = self._getMarkerType()
        return (self._createArcadeMarker(markerType, _CONSTANTS.ARCADE_GUN_MARKER_NAME), self._createSniperMarker(markerType, _CONSTANTS.SNIPER_GUN_MARKER_NAME))

    def _createSPGMarkers(self):
        markerType = self._getMarkerType()
        return (self._createArcadeMarker(markerType, _CONSTANTS.ARCADE_GUN_MARKER_NAME), self._createSPGMarker(markerType, _CONSTANTS.SPG_GUN_MARKER_NAME))

    def _createArcadeMarker(self, markerType, name):
        dataProvider = self._getMarkerDataProvider(markerType)
        return self._createMarker(DefaultGunMarkerComponent, _VIEW_ID.ARCADE, markerType, dataProvider, name)

    def _createSniperMarker(self, markerType, name):
        dataProvider = self._getMarkerDataProvider(markerType)
        return self._createMarker(DefaultGunMarkerComponent, _VIEW_ID.SNIPER, markerType, dataProvider, name)

    def _createSPGMarker(self, markerType, name):
        dataProvider = self._getSPGDataProvider(markerType)
        return self._createMarker(SPGGunMarkerComponent, _VIEW_ID.STRATEGIC, markerType, dataProvider, name)


class _DevControlMarkersFactory(_ControlMarkersFactory):

    def _hasDualAccuracyMarkers(self):
        return self._vehicleInfo.isPlayerVehicle() and self._vehicleInfo.hasDualAccuracy() if self._useDebugMarkers() else super(_DevControlMarkersFactory, self)._hasDualAccuracyMarkers()

    def _useDebugMarkers(self):
        return self._markersInfo.isClientMarkerActivated and self._markersInfo.isServerMarkerActivated

    def _createDefaultMarkers(self):
        return self._createDebugMarkers() if self._useDebugMarkers() else super(_DevControlMarkersFactory, self)._createDefaultMarkers()

    def _createSPGMarkers(self):
        return self._createSPGDebugMarkers() if self._useDebugMarkers() else super(_DevControlMarkersFactory, self)._createSPGMarkers()

    def _createDualGunMarkers(self):
        return self._createDualGunDebugMarkers() if self._useDebugMarkers() else super(_DevControlMarkersFactory, self)._createDualGunMarkers()

    def _createDualGunDebugMarkers(self):
        return (self._createArcadeMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.DUAL_GUN_ARCADE_MARKER_NAME),
         self._createArcadeMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_DUAL_GUN_ARCADE_MARKER_NAME),
         self._createSniperMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.DUAL_GUN_SNIPER_MARKER_NAME),
         self._createSniperMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_DUAL_GUN_SNIPER_MARKER_NAME))

    def _createDebugMarkers(self):
        return (self._createArcadeMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.ARCADE_GUN_MARKER_NAME),
         self._createArcadeMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_ARCADE_GUN_MARKER_NAME),
         self._createSniperMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.SNIPER_GUN_MARKER_NAME),
         self._createSniperMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_SNIPER_GUN_MARKER_NAME))

    def _createSPGDebugMarkers(self):
        return (self._createArcadeMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.ARCADE_GUN_MARKER_NAME),
         self._createArcadeMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_ARCADE_GUN_MARKER_NAME),
         self._createSPGMarker(GUN_MARKER_TYPE.CLIENT, _CONSTANTS.SPG_GUN_MARKER_NAME),
         self._createSPGMarker(GUN_MARKER_TYPE.SERVER, _CONSTANTS.DEBUG_SPG_GUN_MARKER_NAME))


class _EquipmentMarkersFactory(_GunMarkersFactory):

    def create(self):
        return (self._createArtyHitMarker(),) if self._markersInfo.isArtyHitActivated else ()

    def _createArtyHitMarker(self):
        dataProvider = self._markersInfo.clientSPGMarkerDataProvider
        return self._createMarker(SPGGunMarkerComponent, _VIEW_ID.UNDEFINED, GUN_MARKER_TYPE.CLIENT, dataProvider, _CONSTANTS.ARTY_HIT_MARKER_NAME, True)


class _OptionalMarkersFactory(_GunMarkersFactory):

    def create(self):
        return (self._createVideoMarker(),) if self._markersInfo.isEnabledInVideoMode else ()

    def _createVideoMarker(self):
        dataProvider = self._markersInfo.clientMarkerDataProvider
        return self._createMarker(VideoGunMarkerComponent, _VIEW_ID.UNDEFINED, GUN_MARKER_TYPE.CLIENT, dataProvider, _CONSTANTS.VIDEO_GUN_MARKER_NAME, True)


if useDefaultGunMarkers():
    _FACTORIES_COLLECTION = (_ControlMarkersFactory, _OptionalMarkersFactory, _EquipmentMarkersFactory)
else:
    _FACTORIES_COLLECTION = (_DevControlMarkersFactory, _OptionalMarkersFactory, _EquipmentMarkersFactory)

def createComponents(markersInfo, vehicleInfo):
    return _GunMarkersFactories(*_FACTORIES_COLLECTION).create(markersInfo, vehicleInfo)


def overrideComponents(components, markersInfo, vehicleInfo):
    return _GunMarkersFactories(*_FACTORIES_COLLECTION).override(components, markersInfo, vehicleInfo)
