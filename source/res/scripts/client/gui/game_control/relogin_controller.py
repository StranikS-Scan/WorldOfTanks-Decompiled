# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/relogin_controller.py
from debug_utils import LOG_DEBUG
from helpers import dependency
from skeletons.gui.game_control import IReloginController
from skeletons.helpers.statistics import IStatisticsCollector

class ReloginController(IReloginController):
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        super(ReloginController, self).__init__()
        self.__reloginChain = None
        self.__reloginStoppedHandler = None
        return

    def fini(self):
        self.__clearReloginChain()
        super(ReloginController, self).fini()

    def doRelogin(self, peripheryID, onStoppedHandler=None, extraChainSteps=None):
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
        self.statsCollector.needCollectSystemData(True)
        LOG_DEBUG('Relogin finished', isCompleted)
        return

    def __clearReloginChain(self):
        if self.__reloginChain is not None:
            self.__reloginChain.onStopped -= self.__onReloginStopped
            self.__reloginChain.stop()
            self.__reloginChain = None
            self.__reloginStoppedHandler = None
        return
