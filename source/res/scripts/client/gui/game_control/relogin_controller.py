# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/relogin_controller.py
from __future__ import absolute_import
import logging
from helpers import dependency
from skeletons.gui.game_control import IReloginController
from skeletons.helpers.statistics import IStatisticsCollector
_logger = logging.getLogger(__name__)

class ReloginController(IReloginController):
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        super(ReloginController, self).__init__()
        self.__reloginChain = None
        self.__reloginStoppedHandler = None
        return

    @property
    def isActive(self):
        return self.__reloginChain is not None and self.__reloginChain.isActive

    def fini(self):
        self.__clearReloginChain()
        super(ReloginController, self).fini()

    def doRelogin(self, peripheryID, onStoppedHandler=None, extraChainSteps=None):
        from gui.shared import actions
        _logger.debug('Attempt to relogin to the another periphery. peripheryID: %s', peripheryID)
        chain = [actions.LeavePrbModalEntity(), actions.DisconnectFromPeriphery(loginViewPreselectedPeriphery=peripheryID), actions.ConnectToPeriphery(peripheryID)]
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
        _logger.debug('Relogin finished. isCompleted=%s', isCompleted)
        return

    def __clearReloginChain(self):
        if self.__reloginChain is not None:
            self.__reloginChain.onStopped -= self.__onReloginStopped
            self.__reloginChain.stop()
            self.__reloginChain = None
            self.__reloginStoppedHandler = None
        return
