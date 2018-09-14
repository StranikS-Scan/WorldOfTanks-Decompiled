# Embedded file name: scripts/client/gui/miniclient/lobby/hangar/pointcuts.py
import aspects
from helpers import aop

class ShowMiniclientInfo(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.Hangar', 'Hangar', '_populate', aspects=(aspects.ShowMiniclientInfo,))


class DisableTankServiceButtons(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.Hangar', 'Hangar', 'as_setupAmmunitionPanelS', aspects=(aspects.DisableTankServiceButtons(config),))


class MaintenanceButtonFlickering(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel', 'AmmunitionPanel', 'as_setAmmoS', aspects=(aspects.MaintenanceButtonFlickering(config),))


class DeviceButtonsFlickering(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel', 'AmmunitionPanel', 'updateDeviceTooltip', aspects=(aspects.DeviceButtonsFlickering(config),))


class TankModelHangarVisibility(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'CurrentVehicle', '_CurrentVehicle', 'isInHangar', aspects=(aspects.TankModelHangarVisibility(config),))


class TankHangarStatus(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'CurrentVehicle', '_CurrentVehicle', 'getHangarMessage', aspects=(aspects.TankHangarStatus(config),))


class EnableCrew(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.Hangar', 'Hangar', 'as_setCrewEnabledS', aspects=(aspects.EnableCrew(config),))
