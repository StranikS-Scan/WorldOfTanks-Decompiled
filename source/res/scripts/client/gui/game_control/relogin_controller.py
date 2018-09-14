# Embedded file name: scripts/client/gui/game_control/relogin_controller.py
from debug_utils import LOG_DEBUG
from gui.game_control.controllers import Controller

class ReloginController(Controller):

    def __init__(self, proxy):
        super(ReloginController, self).__init__(proxy)
        self.__reloginChain = None
        self.__reloginStoppedHandler = None
        return

    def fini(self):
        self.__clearReloginChain()
        super(ReloginController, self).fini()

    def doRelogin(self, peripheryID, onStoppedHandler = None, extraChainSteps = None):
        from gui.shared import actions
        LOG_DEBUG('Attempt to relogin to the another periphery', peripheryID)
        chain = [actions.LeavePrbModalEntity(), actions.DisconnectFromPeriphery(), actions.ConnectToPeriphery(peripheryID)]
        if extraChainSteps is not None:
            chain += extraChainSteps
        self.__reloginStoppedHandler = onStoppedHandler
        self.__reloginChain = actions.ActionsChain(chain)
        self.__reloginChain.onStopped += self.__onReloginStopped
        self.__reloginChain.start()
        return

    def __onReloginStopped(self, isCompleted):
        if self.__reloginStoppedHandler is not None:
            self.__reloginStoppedHandler(isCompleted)
        LOG_DEBUG('Relogin finished', isCompleted)
        return

    def __clearReloginChain(self):
        if self.__reloginChain is not None:
            self.__reloginChain.onStopped -= self.__onReloginStopped
            self.__reloginChain.stop()
            self.__reloginChain = None
            self.__reloginStoppedHandler = None
        return
