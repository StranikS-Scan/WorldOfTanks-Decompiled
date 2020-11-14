# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_info_components/vehicles_area_marker_info.py


class VehiclesAreaMarkerInfo(object):

    def onEnterWorld(self):
        self._setVehiclesAreaMarkerParams()

    def onLeaveWorld(self):
        pass

    def set_vehiclesAreaMarkerParams(self, _):
        self._setVehiclesAreaMarkerParams()

    def _setVehiclesAreaMarkerParams(self):
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if self.vehiclesAreaMarkerParams is not None and areaMarkerCtrl:
            areaMarkerCtrl.setVehiclesAreaMarkerParams(self.vehiclesAreaMarkerParams)
        return
