# Embedded file name: scripts/client/gui/miniclient/lobby/tank_carousel/aspects.py
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.shared.gui_items.Vehicle import Vehicle

class VehicleTooltipStatus(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if not self.__vehicle_is_available(cd.args[2]):
            cd.avoid()
            return {'header': _ms('#menu:tankCarousel/vehicleStates/%s' % Vehicle.VEHICLE_STATE.UNAVAILABLE),
             'text': '',
             'level': Vehicle.VEHICLE_STATE_LEVEL.CRITICAL}


class MakeTankUnavailableInCarousel(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        cd.change()
        original_args = list(cd.args)

        class vehicleItemMock:
            level = 0
            isPremium = False

        for intCD, vehicleData in original_args[0].iteritems():
            vehicleItemMock.level = vehicleData['level']
            vehicleItemMock.isPremium = vehicleData['premium']
            if not self.__vehicle_is_available(vehicleItemMock):
                vehicleData['stat'] = str(Vehicle.VEHICLE_STATE.UNAVAILABLE)
                vehicleData['stateLevel'] = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                vehicleData['statStr'] = cd.self.getStringStatus(Vehicle.VEHICLE_STATE.UNAVAILABLE)

        return (original_args, cd.kwargs)
