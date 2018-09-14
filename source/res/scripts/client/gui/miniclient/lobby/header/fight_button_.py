# Embedded file name: scripts/client/gui/miniclient/lobby/header/fight_button_.py
from helpers import aop
from CurrentVehicle import g_currentVehicle

class _DisableFightButtonAspect(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        if g_currentVehicle.isPresent() and not self.__vehicle_is_available(g_currentVehicle.item):
            cd.change()
            original_args = list(cd.args)
            original_args[0] = True
            return (original_args, cd.kwargs)


class DisableFightButtonPointcut(aop.Pointcut):

    def __init__(self, config):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header.LobbyHeader', 'LobbyHeader', 'as_disableFightButtonS', aspects=(_DisableFightButtonAspect(config),))
