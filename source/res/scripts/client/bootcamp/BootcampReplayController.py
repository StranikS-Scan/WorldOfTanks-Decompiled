# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampReplayController.py
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
import BattleReplay
BOOTCAMP_REPLAY_EVENTS = ('bootcampMarkers_onTriggerActivated', 'bootcampMarkers_onTriggerDeactivated', 'bootcampMarkers_showMarker', 'bootcampMarkers_hideMarker', 'bootcampHint_show', 'bootcampHint_hide', 'bootcampHint_complete', 'bootcampHint_close', 'bootcampHint_onHided')

class BootcampReplayControllerQueue:

    def __init__(self, name):
        self.__name = name
        self.__data = []
        self.__callback = None
        return

    def init(self):
        BattleReplay.g_replayCtrl.setDataCallback(self.__name, self.replayCallbackeMethod)

    def fini(self):
        BattleReplay.g_replayCtrl.delDataCallback(self.__name, self.replayCallbackeMethod)
        self.__callback = None
        return

    def replayCallbackeMethod(self, binData):
        if self.__callback is not None:
            return self.__callback(binData)
        else:
            self.__data.append(binData)
            return

    def setDataCallback(self, callback):
        self.__callback = callback
        for binData in self.__data:
            callback(binData)

        self.__data = []

    def delDataCallback(self, callback):
        if callback is not self.__callback:
            LOG_DEBUG_DEV_BOOTCAMP('Multiple callback unsubscribe:', self.__name)
            return
        else:
            self.__callback = None
            return


class BootcampReplayController:

    def __init__(self):
        self.__queues = {}
        for name in BOOTCAMP_REPLAY_EVENTS:
            self.__queues[name] = BootcampReplayControllerQueue(name)

    def init(self):
        for quque in self.__queues.itervalues():
            quque.init()

    def fini(self):
        for quque in self.__queues.itervalues():
            quque.fini()

    def setDataCallback(self, eventName, callback):
        if eventName not in self.__queues:
            LOG_DEBUG_DEV_BOOTCAMP('Failed to set replay data callback:', eventName)
            return
        queue = self.__queues[eventName]
        queue.setDataCallback(callback)

    def delDataCallback(self, eventName, callback):
        if eventName not in self.__queues:
            LOG_DEBUG_DEV_BOOTCAMP('Failed to del replay data callback:', eventName)
            return
        queue = self.__queues[eventName]
        queue.delDataCallback(callback)
