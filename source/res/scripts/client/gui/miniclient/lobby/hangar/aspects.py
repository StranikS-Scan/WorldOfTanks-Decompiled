# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/hangar/aspects.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MINICLIENT import MINICLIENT
from helpers import aop, dependency
from helpers.i18n import makeString as _ms
from CurrentVehicle import g_currentVehicle
from gui.shared.formatters import icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from skeletons.gui.game_control import IBootcampController

class ShowMiniclientInfo(aop.Aspect):
    bootcampController = dependency.descriptor(IBootcampController)

    def atReturn(self, cd):
        if not self.bootcampController.isInBootcamp():
            cd.self.as_showMiniClientInfoS(_ms('#miniclient:hangar/warn_message'), _ms('#miniclient:hangar/continue_download'))


class DisableTankServiceButtons(aop.Aspect):

    def __init__(self, config):
        self.__config = config
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        tooltip = makeTooltip(None, None, None, self.__config.get('sandbox_platform_message', MINICLIENT.AMMUNITION_PANEL_WARN_TOOLTIP))
        if g_currentVehicle.isPresent() and not self.__config['vehicle_is_available'](g_currentVehicle.item):
            cd.change()
            return ((False,
              tooltip,
              False,
              tooltip), cd.kwargs)
        else:
            return


class MaintenanceButtonFlickering(aop.Aspect):

    def __init__(self, config):
        self.__config = config
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__config['vehicle_is_available'](g_currentVehicle.item):
            original_args = list(cd._args)
            shells = original_args[0]
            original_args[1] = False
            for shell in shells:
                shell['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
                shell['tooltip'] = makeTooltip(None, None, None, self.__config.get('sandbox_platform_message', MINICLIENT.AMMUNITION_PANEL_WARN_TOOLTIP))

            cd.change()
            return (original_args, cd.kwargs)
        else:
            return


class DeviceButtonsFlickering(aop.Aspect):

    def __init__(self, config):
        self.__config = config
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__config['vehicle_is_available'](g_currentVehicle.item):
            original_args = list(cd._args)
            devices = original_args[0]['devices']
            for device in devices:
                device['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
                device['tooltip'] = makeTooltip(None, None, None, self.__config.get('sandbox_platform_message', MINICLIENT.AMMUNITION_PANEL_WARN_TOOLTIP))

            cd.change()
            return (original_args, cd.kwargs)
        else:
            return


class TankModelHangarVisibility(aop.Aspect):

    def __init__(self, config):
        self.__config = config
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__config['vehicle_is_available'](g_currentVehicle.item):
            cd.avoid()
            return False
        else:
            return None


class TankHangarStatus(aop.Aspect):

    def __init__(self, config):
        self.__config = config
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__config['vehicle_is_available'](g_currentVehicle.item):
            cd.avoid()
            return (Vehicle.VEHICLE_STATE.NOT_PRESENT, _ms(self.__config.get('sandbox_platform_message', '#miniclient:hangar/unavailable')), Vehicle.VEHICLE_STATE_LEVEL.CRITICAL)
        else:
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


class ChangeLobbyMenuTooltip(aop.Aspect):

    def atReturn(self, cd):
        original = cd.returned
        original['tooltip'] = makeTooltip(TOOLTIPS.LOBBYMENU_VERSIONINFOBUTTON_MINICLIENT_HEADER, TOOLTIPS.LOBBYMENU_VERSIONINFOBUTTON_MINICLIENT_BODY)
        return original
