# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/hangar/__init__.py
import pointcuts as _pointcuts

def configure_pointcuts(config):
    _pointcuts.DisableTankServiceButtons(config)
    _pointcuts.MaintenanceButtonFlickering(config)
    _pointcuts.DeviceButtonsFlickering(config)
    _pointcuts.ShowMiniclientInfo()
    _pointcuts.TankHangarStatus(config)
    _pointcuts.TankModelHangarVisibility(config)
    _pointcuts.EnableCrew(config)
    _pointcuts.ChangeLobbyMenuTooltip()
