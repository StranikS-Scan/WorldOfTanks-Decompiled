# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cam_settings.py
from account_helpers.settings_core.options import HangarCamPeriodSetting
OPTIONS = HangarCamPeriodSetting.OPTIONS
HANGAR_CAM_PERIODS = {OPTIONS.TYPE0: 30,
 OPTIONS.TYPE1: 45,
 OPTIONS.TYPE2: 60}

def convertSettingToFeatures(value):
    selected = OPTIONS.HANGAR_CAM_TYPES[value]
    return HANGAR_CAM_PERIODS.get(selected, -1)
