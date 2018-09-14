# Embedded file name: scripts/client/gui/miniclient/lobby/tank_carousel/pointcuts.py
from helpers import aop
import aspects

class MakeTankUnavailableInCarousel(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.hangar.TankCarousel', 'TankCarousel', '_getVehicleData', aspects=(aspects.MakeTankUnavailableInCarousel(config),))


class VehicleTooltipStatus(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.shared.tooltips.vehicle', 'VehicleStatusField', '_VehicleStatusField__getVehicleStatus', aspects=(aspects.VehicleTooltipStatus(config),))
