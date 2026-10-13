# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/scheduler.py
from __future__ import absolute_import
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from shared_utils import nextTick
from helpers import dependency
from halloween.skeletons.halloween_controller import IHalloweenController

class HalloweenBattleScheduler(BaseScheduler):
    __halloweenBattleCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, entity):
        super(HalloweenBattleScheduler, self).__init__(entity)
        self._isLeaveRequestSent = False

    def init(self):
        self.__halloweenBattleCtrl.onEventDisabled += self.__onEventDisabled
        self.__halloweenBattleCtrl.onSettingsUpdate += self.__onSettingsUpdate

    def fini(self):
        self.__halloweenBattleCtrl.onEventDisabled -= self.__onEventDisabled
        self.__halloweenBattleCtrl.onSettingsUpdate -= self.__onSettingsUpdate

    def _doLeave(self):
        if self._entity and self._entity.isInQueue():
            if not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self._showRandomHangar()
            self._isLeaveRequestSent = False

    def _showRandomHangar(self):
        self.__halloweenBattleCtrl.selectRandomMode()

    def __onEventDisabled(self):
        nextTick(self._doLeave)()

    def __onSettingsUpdate(self):
        g_eventDispatcher.updateUI()
