# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/tank_carousel/aspects.py
from helpers import aop
from helpers.i18n import makeString as _ms
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.formatters import text_styles

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

    def atReturn(self, cd):
        original_return_value = cd.returned
        original_args = cd.args
        if not self.__vehicle_is_available(original_args[0]):
            state = _ms('#menu:tankCarousel/vehicleStates/%s' % Vehicle.VEHICLE_STATE.UNAVAILABLE)
            original_return_value['showInfoText'] = True
            original_return_value['infoText'] = text_styles.vehicleStatusCriticalText(state)
        return original_return_value
