# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/first_of_april_controller.py
from functools import partial
import math
import BigWorld
import weakref
from constants import FIRST_APRIL_ACTIONS
from debug_utils import LOG_DEBUG
from gui.battle_control.arena_info.interfaces import IArenaFirstOfAprilController
from gui.battle_control.avatar_getter import getSoundNotifications
from helpers import time_utils

class _NoSoundNotification(object):

    def __init__(self):
        super(_NoSoundNotification, self).__init__()

    def play(self, soundNotifications):
        pass


class _SoundNotification(_NoSoundNotification):

    def __init__(self, soundEvent):
        super(_SoundNotification, self).__init__()
        self._soundEvent = soundEvent

    def play(self, soundNotifications):
        soundNotifications.play(self._soundEvent)


class _OnceSoundNotification(_SoundNotification):

    def __init__(self, soundEvent):
        super(_OnceSoundNotification, self).__init__(soundEvent)
        self.__isPlayed = False

    def play(self, soundNotifications):
        if not self.__isPlayed:
            self.__isPlayed = True
            soundNotifications.play(self._soundEvent)


ACTIONS_SOUNDS = {FIRST_APRIL_ACTIONS.JUMP: 'first_of_april_jump',
 FIRST_APRIL_ACTIONS.COMPULSE: 'first_of_april_impulse',
 FIRST_APRIL_ACTIONS.ARTILLERY: 'first_of_april_meteor',
 FIRST_APRIL_ACTIONS.EMPTY: 'first_of_april_empty'}

class FirstOfAprilController(IArenaFirstOfAprilController):

    def __init__(self):
        super(FirstOfAprilController, self).__init__()
        self.__panel = None
        self.__currentActionID = None
        self.__currentActionTime = 0
        self.__currentActionSound = _NoSoundNotification()
        self.__callbackID = None
        self.__soundCallbackID = None
        self.__soundNotifications = None
        self.__notificationSndName = 'first_of_april_notification'
        return

    def start(self, panel):
        self.__panel = panel
        self.__soundNotifications = weakref.proxy(getSoundNotifications())
        if self.__currentActionID is not None:
            self.__start()
        return

    def stop(self):
        self.__panel = None
        self.__soundNotifications = None
        if self.__callbackID is not None:
            self.__cancelCallback()
        if self.__soundCallbackID is not None:
            self.__cancelSoundCallback()
        return

    def processAction(self, actionID, actionTime):
        self.__currentActionID = actionID
        self.__currentActionTime = actionTime
        self.__currentActionSound = _NoSoundNotification()
        if actionID != FIRST_APRIL_ACTIONS.UNKNOWN:
            soundName = ACTIONS_SOUNDS[actionID]
            if actionID != FIRST_APRIL_ACTIONS.EMPTY:
                self.__currentActionSound = _SoundNotification(self.__notificationSndName)
                self.__soundCallbackID = BigWorld.callback(self.__getTimeLeft(), partial(self.__soundCallback, soundName))
            else:
                self.__currentActionSound = _OnceSoundNotification(soundName)
        if self.__panel is not None:
            if self.__callbackID is None:
                self.__start()
        LOG_DEBUG('Action is processed: ', self.__currentActionID, self.__getTimeLeft())
        return

    def __start(self):
        self.__panel.show(self.__currentActionID, self.__getTimeLeftStr())
        timeLeft = self.__getTimeLeft()
        timeTilFullSecond = timeLeft - math.floor(timeLeft)
        if timeTilFullSecond:
            self.__callbackID = BigWorld.callback(timeTilFullSecond, self.__callback)
        else:
            self.__callbackID = BigWorld.callback(1.0, self.__callback)

    def __callback(self):
        if self.__getTimeLeft() > 0:
            self.__currentActionSound.play(self.__soundNotifications)
            self.__panel.update(self.__currentActionID, self.__getTimeLeftStr())
            self.__callbackID = BigWorld.callback(1.0, self.__callback)
        else:
            self.__panel.hide()
            self.__cancelCallback()

    def __soundCallback(self, soundName):
        self.__cancelSoundCallback()
        self.__soundNotifications.play(soundName)

    def __cancelCallback(self):
        self.__currentActionID = None
        self.__currentActionTime = 0
        self.__currentActionSound = _NoSoundNotification()
        BigWorld.cancelCallback(self.__callbackID)
        self.__callbackID = None
        return

    def __cancelSoundCallback(self):
        BigWorld.cancelCallback(self.__soundCallbackID)
        self.__soundCallbackID = None
        return

    def __getTimeLeft(self):
        return max(0, self.__currentActionTime - BigWorld.serverTime())

    def __getTimeLeftStr(self):
        return time_utils.getTimeLeftFormat(math.ceil(self.__getTimeLeft()))
