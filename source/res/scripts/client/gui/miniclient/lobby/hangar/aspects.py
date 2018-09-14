# Embedded file name: scripts/client/gui/miniclient/lobby/hangar/aspects.py
from helpers import aop
from helpers.i18n import makeString as _ms
from CurrentVehicle import g_currentVehicle
from gui.shared.formatters import icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.locale.MENU import MENU

class ShowMiniclientInfo(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS(_ms('#miniclient:hangar/warn_message'), _ms('#miniclient:hangar/continue_download'))


class DisableTankServiceButtons(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        tooltip = makeTooltip(None, '{0} {1}'.format(icons.alert(-3), _ms('#miniclient:ammunition_panel/warn_tooltip')))
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            cd.change()
            return ((False,
              tooltip,
              False,
              tooltip), cd.kwargs)
        else:
            return
            return


class MaintenanceButtonFlickering(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            original_args = list(cd._args)
            original_args[0]['stateWarning'] = 0
            cd.change()
            return (original_args, cd.kwargs)
        else:
            return None
            return None


class TankModelHangarVisibility(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            cd.avoid()
            return False
        else:
            return None
            return None


class TankHangarStatus(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            cd.avoid()
            return (Vehicle.VEHICLE_STATE.NOT_PRESENT, _ms('#miniclient:hangar/unavailable'), Vehicle.VEHICLE_STATE_LEVEL.CRITICAL)
        else:
            return None
            return None


class EnableCrew(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            cd.change()
            return ([True], {})
        else:
            return None
            return None
