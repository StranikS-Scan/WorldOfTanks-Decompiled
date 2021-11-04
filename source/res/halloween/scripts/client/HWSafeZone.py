# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWSafeZone.py
import logging
import BigWorld
import Math
from account_helpers.settings_core import settings_constants
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import SafeZoneMarker
from gui.shared.gui_items.marker_items import MarkerItem
from gui.shared.gui_items.marker_items import MarkerParamsFactory
from PlayerEvents import g_playerEvents
_logger = logging.getLogger(__name__)
_SETTINGS_DRAW_TYPE_MAP = {0: 1,
 1: 0,
 2: 0}
_DEFAULT_SAFEZONE_BORER_TYPE = 0

class HWSafeZone(BigWorld.Entity):
    _BORDER_ID = 0
    _BORDER_COLOR = (1.0, 0.0, 0.0, 1.0)
    _BORDER_HEIGHT = 20
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(HWSafeZone, self).__init__()
        _logger.info('[HWSafeZone.__init__] %s %s', str(self.isActive), str(self.geometry))
        self._hasBorder = False
        self._areaMarkerCtrl = self.guiSessionProvider.shared.areaMarker
        self._marker = None
        if getattr(self, 'vehiclesUnderFire', None) is None:
            self.vehiclesUnderFire = []
        g_playerEvents.onAvatarReady += self._onAvatarReady
        return

    def set_isActive(self, prev=None):
        _logger.info('[HWSafeZone.set_isActive] %d', int(self.isActive))
        self._updateBorders()
        self._updateMarker()

    def set_geometry(self, prev=None):
        _logger.info('[HWSafeZone.set_geometry] %s', str(self.geometry))
        self._updateBorders()
        self._updateMarker()

    def setSlice_vehiclesUnderFire(self, changePath, oldValue):
        _logger.info('[HWSafeZone.setSlice_vehiclesUnderFire]: vehiclesUnderFire %s, changePath %s', str(self.vehiclesUnderFire), str(changePath))
        self._updateDestroyTimer()

    def setNested_vehiclesUnderFire(self, path, oldValue):
        _logger.info('[HWSafeZone.setNested_vehiclesUnderFire]: vehiclesUnderFire %s, path %s', str(self.vehiclesUnderFire), str(path))
        self._updateDestroyTimer()

    def onEnterWorld(self, prereqs):
        self._createMarker()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def onLeaveWorld(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        self._destroyBorders()
        self._destroyMarker()

    def _onAvatarReady(self):
        self._createBorders()
        self._updateDestroyTimer()

    @property
    def _spaceID(self):
        player = BigWorld.player()
        return player.spaceID if player and player.spaceID else None

    def _createBorders(self):
        if self._hasBorder:
            return
        else:
            spaceID = self._spaceID
            if spaceID is None:
                return
            self._hasBorder = True
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, self._BORDER_ID, Math.Vector3(self.geometry[0], 0, self.geometry[2]), self._calculateBorderBounds(self.geometry[3:]))
            BigWorld.ArenaBorderHelper.setBorderHeight(spaceID, self._BORDER_ID, self._BORDER_HEIGHT)
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self._BORDER_ID, self._BORDER_COLOR)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self._BORDER_ID, self.isActive)
            self.__applyBorderType()
            return

    def _destroyBorders(self):
        if not self._hasBorder:
            return
        else:
            spaceID = self._spaceID
            if spaceID is None:
                return
            self._hasBorder = False
            BigWorld.ArenaBorderHelper.removeBorder(spaceID, self._BORDER_ID)
            return

    def _updateBorders(self):
        spaceID = self._spaceID
        if spaceID is None or not self._hasBorder:
            return
        else:
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self._BORDER_ID, self.isActive)
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, self._BORDER_ID, Math.Vector3(self.geometry[0], 0, self.geometry[2]), self._calculateBorderBounds(self.geometry[3:]))
            return

    def _createMarker(self):
        ctrl = self.guiSessionProvider.shared.areaMarker
        if not ctrl:
            return
        createParams = MarkerParamsFactory.getMarkerParams(self.matrix, MarkerItem.SAFEZONE, 0)
        createParams['visible'] = self.isActive
        createParams['size'] = self.geometry[3:]
        self._marker = SafeZoneMarker(createParams)
        ctrl.addMarker(self._marker)

    def _destroyMarker(self):
        ctrl = self.guiSessionProvider.shared.areaMarker
        if not ctrl:
            return
        else:
            ctrl.removeMarker(self._marker.markerID)
            self._marker = None
            return

    def _updateMarker(self):
        ctrl = self.guiSessionProvider.shared.areaMarker
        if not ctrl:
            return
        self._marker.setSize(self.geometry[3:])
        if self.isActive:
            ctrl.showMarkersById(self._marker.markerID)
        else:
            ctrl.hideMarkersById(self._marker.markerID)

    def _updateDestroyTimer(self):
        avatar = BigWorld.player()
        if not avatar:
            return
        else:
            enabled = False
            nextStrikeTime = 0.0
            waveDuration = 0.0
            vehicleId = BigWorld.player().playerVehicleID
            vehUnderFire = next((v for v in self.vehiclesUnderFire if v['vehicleId'] == vehicleId), None)
            if vehUnderFire is not None:
                enabled = True
                nextStrikeTime = vehUnderFire['nextStrikeTime']
                waveDuration = vehUnderFire['waveDuration']
            avatar.updateDeathZoneWarningNotification(enabled, nextStrikeTime, waveDuration)
            return

    @staticmethod
    def _calculateBorderBounds(size):
        return Math.Vector4(-size[0] * 0.5, -size[1] * 0.5, size[0] * 0.5, size[1] * 0.5)

    def __onSettingsChanged(self, diff):
        if settings_constants.BATTLE_BORDER_MAP.TYPE_BORDER in diff:
            self.__applyBorderType()

    def __applyBorderType(self):
        if self._spaceID is None:
            return
        else:
            arenaBorderDrawType = self.settingsCore.getSetting(settings_constants.BATTLE_BORDER_MAP.TYPE_BORDER)
            zoneDrawType = _SETTINGS_DRAW_TYPE_MAP.get(arenaBorderDrawType, _DEFAULT_SAFEZONE_BORER_TYPE)
            BigWorld.ArenaBorderHelper.setBordersDrawType(self._spaceID, self._BORDER_ID, zoneDrawType)
            return
