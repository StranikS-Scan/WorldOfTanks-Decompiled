# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/hw19_vehicle_settings.py
import logging
import ResMgr
from items import vehicles
_logger = logging.getLogger(__name__)
_SETTINGS_XML_PATH = 'gui/hw19_vehicle_settings.xml'
_DEFAULT_MARKER_HEIGHT_FACTOR = 1.0
_DEFAULT_MARKER_STYLE_ID = 1

class EventVehicleSettings(object):

    def __init__(self):
        self._initVehiclSettings()

    def _initVehiclSettings(self):
        self._vehiclesSettings = {}
        self._map = {}
        vehiclesSettings = ResMgr.openSection(_SETTINGS_XML_PATH)
        if vehiclesSettings:
            for vehicle in vehiclesSettings.values():
                cd = vehicles.VehicleDescr(typeName=vehicle['typeName'].asString).type.compactDescr
                self._vehiclesSettings[cd] = {'markerHeightFactor': vehicle['markerHeightFactor'].asFloat,
                 'markerStyleId': vehicle['markerStyleId'].asInt,
                 'icon': vehicle['icon'].asString,
                 'battleResultIcon': vehicle['battleResultIcon'].asString,
                 'header': vehicle['header'].asString,
                 'label': vehicle['label'].asString,
                 'weight': vehicle['weight'].asInt,
                 'questId': vehicle['questId'].asString,
                 'id': cd}
                self._map[vehicle['vehicleTypeID'].asInt] = [vehicle['questId'].asString, vehicle['commanderId'].asString]

        else:
            _logger.error('Failed to open: %s', _SETTINGS_XML_PATH)
        ResMgr.purge(_SETTINGS_XML_PATH, True)

    def getVehiclesSettings(self):
        return self._vehiclesSettings

    def getMap(self):
        return self._map

    def getMarkerHeightFactor(self, typeName):
        cd = vehicles.VehicleDescr(typeName=typeName).type.compactDescr
        return self._vehiclesSettings.get(cd, {}).get('markerHeightFactor', _DEFAULT_MARKER_HEIGHT_FACTOR)

    def getMarkerStyleId(self, typeName):
        cd = vehicles.VehicleDescr(typeName=typeName).type.compactDescr
        return self._vehiclesSettings.get(cd, {}).get('markerStyleId', _DEFAULT_MARKER_STYLE_ID)

    def getTankManIcon(self, cd):
        return self._vehiclesSettings.get(cd, {}).get('icon', '')

    def getTankManBattleResultIcon(self, cd):
        return self._vehiclesSettings.get(cd, {}).get('battleResultIcon', '')

    def getTankManHeader(self, cd):
        return self._vehiclesSettings.get(cd, {}).get('header', '')

    def getTankManLabel(self, cd):
        return self._vehiclesSettings.get(cd, {}).get('label', '')

    def getQuestId(self, cd):
        return self._vehiclesSettings.get(cd, {}).get('questId', '')
