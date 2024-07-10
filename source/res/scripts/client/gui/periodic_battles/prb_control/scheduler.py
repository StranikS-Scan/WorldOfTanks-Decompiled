# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/prb_control/scheduler.py
import BigWorld
from gui.impl import backport
from gui import SystemMessages
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from shared_utils import first

class PeriodicScheduler(BaseScheduler):

    def __init__(self, entity):
        super(PeriodicScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    def init(self):
        self._startListening()
        self._initScheduler()

    def fini(self):
        self._stopListening()

    def _hasConfiguredNotification(self):
        return True

    def _checkEventEnding(self):
        return False

    def _isEventEnded(self):
        return False

    def _getController(self):
        raise NotImplementedError

    def _getMessageParams(self):
        return {}

    def _getPrimeTimeStatus(self, controller=None):
        controller = controller or self._getController()
        return first(controller.getPrimeTimeStatus()) if controller else None

    def _getResRoot(self):
        raise NotImplementedError

    def _checkLeave(self, controller=None, status=None):
        controller = controller or self._getController()
        status = status if status is not None else self._getPrimeTimeStatus(controller)
        if controller is None or status is None or self._checkControllerLeave(controller):
            BigWorld.callback(0.0, self._doLeave)
            return True
        else:
            return False

    def _checkControllerLeave(self, controller):
        return not controller.isAvailable()

    def _doLeave(self):
        if self._entity is None:
            return
        else:
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return

    def _initScheduler(self):
        status = self._getPrimeTimeStatus()
        if self._checkLeave(status=status):
            return
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.__show(isInit=True)

    def _startListening(self):
        self._getController().onGameModeStatusUpdated += self._updateScheduler

    def _stopListening(self):
        self._getController().onGameModeStatusUpdated -= self._updateScheduler

    def _updateScheduler(self, status):
        if self._checkLeave(status=status):
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self, isInit=False):
        controller = self._getController()
        if controller is None or not controller.isBattlesPossible():
            return
        else:
            if not self.__isConfigured and self._hasConfiguredNotification():
                SystemMessages.pushMessage(backport.text(self._getResRoot().notification.notSet(), **self._getMessageParams()), messageData={'title': backport.text(self._getResRoot().notification.notSet.title())}, type=SystemMessages.SM_TYPE.PeriodicBattlesNotSet)
            elif not self.__isPrimeTime:
                msgPath = self._getResRoot().notification.modeEnded() if self._checkEventEnding() and self._isEventEnded() else self._getResRoot().notification.primeTime()
                SystemMessages.pushMessage(backport.text(msgPath, **self._getMessageParams()), messageData={'title': backport.text(self._getResRoot().notification.primeTime.title())}, type=SystemMessages.SM_TYPE.PrimeTime)
            elif not isInit:
                SystemMessages.pushMessage(backport.text(self._getResRoot().notification.available(), **self._getMessageParams()), messageData={'title': backport.text(self._getResRoot().notification.available.title())}, type=SystemMessages.SM_TYPE.PeriodicBattlesAvailable)
            return
