# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/FLReplayController.py
from __future__ import absolute_import
import BattleReplay

class FLReplayController(object):

    def __init__(self):
        pass

    @staticmethod
    def setDataCallback(eventName, callback):
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(eventName, callback)

    @staticmethod
    def delDataCallback(eventName, callback):
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.delDataCallback(eventName, callback)

    @staticmethod
    def serializeCallbackData(eventName, data):
        BattleReplay.g_replayCtrl.serializeCallbackData(eventName, data)
