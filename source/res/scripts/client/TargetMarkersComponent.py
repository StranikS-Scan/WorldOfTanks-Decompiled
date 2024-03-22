# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TargetMarkersComponent.py
import BigWorld
import Math
import TriggersManager
from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class TargetMarkersComponent(DynamicScriptComponent, TriggersManager.ITriggerListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TargetMarkersComponent, self).__init__()
        self._isReconnect = not self._isAvatarReady
        self._markers = {}

    def onDestroy(self):
        TriggersManager.g_manager.delListener(self)
        self._markers.clear()
        super(TargetMarkersComponent, self).onDestroy()

    def addMarker(self, markerSetting):
        targetId = markerSetting['targetId']
        vehicle = BigWorld.entities.get(targetId)
        if vehicle is not None:
            self._createVisibleMarker(targetId, markerSetting, vehicle)
        return

    def removeMarkers(self, markerSettings):
        for settings in markerSettings:
            self._deleteMarkerBySettingId(settings['targetId'], settings['settingId'])

    def onTriggerActivated(self, params):
        triggerType = params.get('type')
        if triggerType not in [TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED, TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED]:
            return
        else:
            vehicleId = params['vehicleId']
            for marker in self._markers.get(vehicleId, {}).values():
                self._deleteMarker(vehicleId, marker)

            if triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
                vehicle = BigWorld.entities.get(vehicleId)
                if vehicle is not None:
                    self._markers[vehicleId] = {}
                    for settings in self.markersSettings:
                        if vehicle.id == settings['targetId']:
                            if params['isVisible']:
                                self._createVisibleMarker(vehicle.id, settings, vehicle)
                            else:
                                self._createInvisibleMarker(vehicle.id, settings, vehicle.position)

            return

    def _onAvatarReady(self):
        TriggersManager.g_manager.addListener(self)
        if self._isReconnect:
            for settings in self.markersSettings:
                targetId = settings['targetId']
                target = BigWorld.entities.get(settings['targetId'])
                lastVisiblePosition = settings['lastVisiblePosition']
                if target is not None:
                    self._createVisibleMarker(targetId, settings, target)
                if lastVisiblePosition:
                    self._createInvisibleMarker(targetId, settings, lastVisiblePosition)

        return

    def _createVisibleMarker(self, vehicleId, settings, vehicle):
        if vehicle and not vehicle.isDestroyed:
            self._createMarker(vehicleId=vehicleId, settingId=settings['settingId'], markerType=settings['visibleStyle'], matrix=vehicle.matrix, vehicle=vehicle)

    def _createInvisibleMarker(self, vehicleId, settings, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        self._createMarker(vehicleId=vehicleId, settingId=settings['settingId'], markerType=settings['invisibleStyle'], matrix=matrix)

    def _createMarker(self, vehicleId, settingId, markerType, matrix, vehicle=None):
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl is None or not markerType:
            return
        else:
            params = {'markerType': markerType,
             'visible': True,
             'matrix': matrix,
             'targetID': vehicleId,
             'entity': vehicle}
            marker = ctrl.createMarker(**params)
            ctrl.addMarker(marker)
            self._markers.setdefault(vehicleId, {})[settingId] = marker
            return

    def _deleteMarker(self, targetId, marker):
        self._removeMarker(marker.markerID)
        settingId = self._getSettingId(targetId, marker)
        if settingId is not None:
            targetMarkers = self._markers.get(targetId, {})
            targetMarkers.pop(settingId)
        return

    def _deleteMarkerBySettingId(self, targetId, settingId):
        targetMarkers = self._markers.get(targetId, {})
        marker = targetMarkers.get(settingId)
        if marker is not None:
            targetMarkers.pop(settingId)
            self._removeMarker(marker.markerID)
        return

    def _getSettingId(self, targetId, marker):
        for sId, m in self._markers.get(targetId, {}).iteritems():
            if m == marker:
                return sId

        return None

    def _removeMarker(self, markerID):
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl is None:
            return
        else:
            ctrl.removeMarker(markerID=markerID)
            return
