# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/nation_change/__init__.py
from constants import ITEM_DEFS_PATH
from NationChangeSettings import NationChangeSettings
g_settings = None
PDATA_NATION_CHANGE_VEHICLE_DOSSIER_KEY = 'nationChangeVehicleDossier'
CONFIG_XML_PATH = ITEM_DEFS_PATH + 'nation_change.xml'
UNDEFINED_ID = -1

def init(settingsXml=CONFIG_XML_PATH):
    global g_settings
    g_settings = NationChangeSettings(settingsXml)


def findVehicleNationGroupId(vehicleTypeName):
    group = g_settings.findVehicleGroup(vehicleTypeName)
    return UNDEFINED_ID if group is None else group.ID
