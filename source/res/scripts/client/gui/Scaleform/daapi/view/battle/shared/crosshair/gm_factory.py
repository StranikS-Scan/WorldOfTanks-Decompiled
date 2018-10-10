# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/crosshair/gm_factory.py
from AvatarInputHandler.aih_constants import GUN_MARKER_TYPE
from AvatarInputHandler.gun_marker_ctrl import useDefaultGunMarkers
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID as _VIEW_ID
from gui.Scaleform.daapi.view.battle.shared.crosshair import gm_components as _components
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _CONSTANTS

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
            result = factory().create(markersInfo, vehicleInfo, components=components)
            if result:
                markers = markers + result

        return _components.GunMarkersComponents(markers)


class _GunMarkersFactory(object):

    def create(self, markersInfo, vehicleInfo, components=None):
        raise NotImplementedError

    @staticmethod
    def _findComponent(markerType, dataProvider, components, name):
        component = None
        if components is not None:
            component = components.popComponent(name)
            if component is not None:
                component.setDataProvider(markerType, dataProvider)
        return component


class _ControlMarkersFactory(_GunMarkersFactory):

    def create(self, markersInfo, vehicleInfo, components=None):
        if vehicleInfo.isSPG():
            markers = self._createSPGMarkers(markersInfo, components=components)
        else:
            markers = self._createDefaultMarkers(markersInfo, components=components)
        return markers

    def _createDefaultMarkers(self, markersInfo, components=None):
        if markersInfo.isServerMarkerActivated:
            dataProvider = markersInfo.serverMarkerDataProvider
            markerType = GUN_MARKER_TYPE.SERVER
        elif markersInfo.isClientMarkerActivated:
            dataProvider = markersInfo.clientMarkerDataProvider
            markerType = GUN_MARKER_TYPE.CLIENT
        else:
            dataProvider = None
            markerType = GUN_MARKER_TYPE.UNDEFINED
        return (self._createArcadeMarker(markerType, dataProvider, components=components), self._createSniperMarker(markerType, dataProvider, components=components))

    def _createSPGMarkers(self, markersInfo, components=None):
        if markersInfo.isServerMarkerActivated:
            dataProvider = markersInfo.serverMarkerDataProvider
            spgDataProvider = markersInfo.serverSPGMarkerDataProvider
            markerType = GUN_MARKER_TYPE.SERVER
        elif markersInfo.isClientMarkerActivated:
            dataProvider = markersInfo.clientMarkerDataProvider
            spgDataProvider = markersInfo.clientSPGMarkerDataProvider
            markerType = GUN_MARKER_TYPE.CLIENT
        else:
            dataProvider = None
            spgDataProvider = None
            markerType = GUN_MARKER_TYPE.UNDEFINED
        return (self._createArcadeMarker(markerType, dataProvider, components=components), self._createSPGMarker(markerType, spgDataProvider, components=components))

    def _createArcadeMarker(self, markerType, dataProvider, components=None, name=_CONSTANTS.ARCADE_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_LINKAGE):
        component = self._findComponent(markerType, dataProvider, components, name)
        if component is None:
            component = _components.DefaultGunMarkerComponent(markerType, _VIEW_ID.ARCADE, name, linkage, dataProvider)
        return component

    def _createSniperMarker(self, markerType, dataProvider, components=None, name=_CONSTANTS.SNIPER_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_LINKAGE):
        component = self._findComponent(markerType, dataProvider, components, name)
        if component is None:
            component = _components.DefaultGunMarkerComponent(markerType, _VIEW_ID.SNIPER, name, linkage, dataProvider)
        return component

    def _createSPGMarker(self, markerType, dataProvider, components=None, name=_CONSTANTS.SPG_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_SPG_LINKAGE):
        component = self._findComponent(markerType, dataProvider, components, name)
        if component is None:
            component = _components.SPGGunMarkerComponent(markerType, _VIEW_ID.STRATEGIC, name, linkage, dataProvider)
        return component


class _DevControlMarkersFactory(_ControlMarkersFactory):

    def _createDefaultMarkers(self, markersInfo, components=None):
        return self._createDebugMarkers(markersInfo, components=components) if markersInfo.isClientMarkerActivated and markersInfo.isServerMarkerActivated else super(_DevControlMarkersFactory, self)._createDefaultMarkers(markersInfo, components=components)

    def _createSPGMarkers(self, markersInfo, components=None):
        return self._createSPGDebugMarkers(markersInfo, components=components) if markersInfo.isClientMarkerActivated and markersInfo.isServerMarkerActivated else super(_DevControlMarkersFactory, self)._createSPGMarkers(markersInfo, components=components)

    def _createDebugMarkers(self, markersInfo, components=None):
        return (self._createArcadeMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientMarkerDataProvider, components=components),
         self._createArcadeMarker(GUN_MARKER_TYPE.SERVER, markersInfo.serverMarkerDataProvider, components=components, name=_CONSTANTS.DEBUG_ARCADE_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_DEBUG_LINKAGE),
         self._createSniperMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientMarkerDataProvider, components=components),
         self._createSniperMarker(GUN_MARKER_TYPE.SERVER, markersInfo.serverMarkerDataProvider, components=components, name=_CONSTANTS.DEBUG_SNIPER_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_DEBUG_LINKAGE))

    def _createSPGDebugMarkers(self, markersInfo, components):
        return (self._createArcadeMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientMarkerDataProvider, components=components),
         self._createArcadeMarker(GUN_MARKER_TYPE.SERVER, markersInfo.serverMarkerDataProvider, components=components, name=_CONSTANTS.DEBUG_ARCADE_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_DEBUG_LINKAGE),
         self._createSPGMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientSPGMarkerDataProvider, components=components),
         self._createSPGMarker(GUN_MARKER_TYPE.SERVER, markersInfo.serverSPGMarkerDataProvider, components=components, name=_CONSTANTS.DEBUG_SPG_GUN_MARKER_NAME, linkage=_CONSTANTS.GUN_MARKER_SPG_DEBUG_LINKAGE))


class _EquipmentMarkersFactory(_GunMarkersFactory):

    def create(self, markersInfo, vehicleInfo, components=None):
        return (self._createArtyHitMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientSPGMarkerDataProvider, components),) if markersInfo.isArtyHitActivated else ()

    def _createArtyHitMarker(self, markerType, dataProvider, components=None, name=_CONSTANTS.ARTY_HIT_MARKER_NAME):
        component = self._findComponent(markerType, dataProvider, components, name)
        if component is None:
            component = _components.SPGGunMarkerComponent(markerType, _VIEW_ID.UNDEFINED, name, _CONSTANTS.ARTY_HIT_MARKER_LINKAGE, dataProvider, isActive=True)
        return component


class _OptionalMarkersFactory(_GunMarkersFactory):

    def create(self, markersInfo, vehicleInfo, components=None):
        return (self._createVideoMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientMarkerDataProvider, components),) if markersInfo.isEnabledInVideoMode else ()

    def _createVideoMarker(self, markerType, dataProvider, components=None, name=_CONSTANTS.VIDEO_GUN_MARKER_NAME):
        component = self._findComponent(markerType, dataProvider, components, name)
        if component is None:
            component = _components.VideoGunMarkerComponent(markerType, _VIEW_ID.UNDEFINED, name, _CONSTANTS.GUN_MARKER_LINKAGE, dataProvider, isActive=True)
        return component


if useDefaultGunMarkers():
    _FACTORIES_COLLECTION = (_ControlMarkersFactory, _OptionalMarkersFactory, _EquipmentMarkersFactory)
else:
    _FACTORIES_COLLECTION = (_DevControlMarkersFactory, _OptionalMarkersFactory, _EquipmentMarkersFactory)

def createComponents(markersInfo, vehicleInfo):
    return _GunMarkersFactories(*_FACTORIES_COLLECTION).create(markersInfo, vehicleInfo)


def overrideComponents(components, markersInfo, vehicleInfo):
    return _GunMarkersFactories(*_FACTORIES_COLLECTION).override(components, markersInfo, vehicleInfo)
