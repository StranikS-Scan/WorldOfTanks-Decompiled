# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/training/legacy/requester.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import PREBATTLE_TYPE, PREBATTLE_CACHE_KEY
from debug_utils import LOG_ERROR
from gui.prb_control.entities.base.requester import IPrbListRequester
from gui.prb_control.items import prb_seqs

class TrainingListRequester(IPrbListRequester):
    UPDATE_LIST_TIMEOUT = 5

    def __init__(self):
        super(TrainingListRequester, self).__init__()
        self.__callbackID = None
        self.__callback = None
        return

    def start(self, callback):
        if self.__callbackID is not None:
            LOG_ERROR('TrainingListRequester already started')
            return
        else:
            if callback is not None and callable(callback):
                g_playerEvents.onPrebattlesListReceived += self.__pe_onPrebattlesListReceived
                self.__callback = callback
                self.__request()
            else:
                LOG_ERROR('Callback is None or is not callable')
                return
            return

    def stop(self):
        g_playerEvents.onPrebattlesListReceived -= self.__pe_onPrebattlesListReceived
        self.__callback = None
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def request(self, ctx=None):
        self.__request()

    def __request(self):
        self.__callbackID = None
        if hasattr(BigWorld.player(), 'requestPrebattles'):
            BigWorld.player().requestPrebattles(PREBATTLE_TYPE.TRAINING, PREBATTLE_CACHE_KEY.CREATE_TIME, False, 0, 50)
        return

    def __setTimeout(self):
        self.__callbackID = BigWorld.callback(self.UPDATE_LIST_TIMEOUT, self.__request)

    def __pe_onPrebattlesListReceived(self, prbType, count, prebattles):
        if prbType != PREBATTLE_TYPE.TRAINING:
            return
        self.__callback(prb_seqs.PrbListIterator(prebattles))
        self.__setTimeout()
