# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/preview.py
from helpers import aop

class ChangeVehicleIsPreviewAllowed(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.shared.gui_items.Vehicle', 'Vehicle', 'isPreviewAllowed', aspects=(_ChangedIsPreviewAllowed(config),))


class _ChangedIsPreviewAllowed(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        vehicle = cd.self
        cd.avoid()
        return self.__vehicle_is_available(vehicle) and cd.function(cd.self)
