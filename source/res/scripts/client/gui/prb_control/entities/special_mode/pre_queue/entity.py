# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/special_mode/pre_queue/entity.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueSubscriber, PreQueueEntryPoint
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.prime_time_constants import PrimeTimeStatus
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class SpecialModeSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class SpecialModeEntryPoint(PreQueueEntryPoint):

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.NOT_AVAILABLE)


class SpecialModeEntity(PreQueueEntity):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, modeFlags, queueType, subscriber, watcherClass):
        super(SpecialModeEntity, self).__init__(modeFlags, queueType, subscriber)
        self._watcherClass = watcherClass
        self.__watcher = None
        return

    @property
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = self._watcherClass()
        self.__watcher.start()
        result = super(SpecialModeEntity, self).init(ctx)
        if not result & FUNCTIONAL_FLAG.LOAD_PAGE:
            result |= self.__processWelcome()
        return result

    def fini(self, ctx=None, woEvents=False):
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(SpecialModeEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(SpecialModeEntity, self).leave(ctx, callback)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(SpecialModeEntity, self).queue(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _isNeedToShowWelcome(self):
        return False

    def _showWelcomeGui(self):
        pass

    def __processWelcome(self):
        if self._isNeedToShowWelcome():
            self._showWelcomeGui()
            return FUNCTIONAL_FLAG.LOAD_PAGE
        return FUNCTIONAL_FLAG.UNDEFINED
