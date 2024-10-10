# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_spam_ctrl/battle_spam_ctrl.py
import BigWorld
import typing
from gui.battle_control.arena_info.interfaces import IBattleSpamController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.battle_spam_ctrl.spam_constants import SpamEvents, SPAM_COOLDOWNS, DEFAULT_COOLDOWN

class BattleSpamController(IBattleSpamController):
    __slots__ = ('__cooldownMgr',)

    def __init__(self):
        self.__cooldownMgr = SpamCooldownManager()

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__cooldownMgr.destroy()

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_SPAM_CTRL

    @staticmethod
    def getSpamCooldown(spamEvent):
        return SPAM_COOLDOWNS.get(spamEvent, DEFAULT_COOLDOWN)

    def filterFullscreenEffects(self, attackerID):
        return self.__filterEvent(SpamEvents.FULLSCREEN_EFFECT, (SpamEvents.FULLSCREEN_EFFECT, attackerID))

    def filterMarkersHitState(self, targetID, stateKey):
        return self.__filterEvent(SpamEvents.MARKERS_HIT_STATE, (SpamEvents.MARKERS_HIT_STATE, targetID, stateKey))

    def filterTeamHealthBarUpdate(self, vehicleID):
        return self.__filterEvent(SpamEvents.TEAM_HEALTH_BAR_UPDATE, (SpamEvents.TEAM_HEALTH_BAR_UPDATE, vehicleID), False)

    def filterShotResultSound(self, vehicleID):
        return self.__filterEvent(SpamEvents.SHOT_RESULT_SOUND, (SpamEvents.SHOT_RESULT_SOUND, vehicleID), False)

    def __filterEvent(self, eventID, eventKey=None, adjustCooldown=True):
        eventKey = eventKey or eventID
        canPlayEvent = not self.__cooldownMgr.isInProcess(eventKey)
        if canPlayEvent or adjustCooldown:
            self.__cooldownMgr.process(eventKey, SPAM_COOLDOWNS.get(eventID))
        return canPlayEvent


class SpamCooldownManager(object):
    __slots__ = ('__cooldowns',)

    def __init__(self):
        self.__cooldowns = {}

    def destroy(self):
        self.__cooldowns.clear()

    def isInProcess(self, eventKey):
        return self.__cooldowns[eventKey] > BigWorld.time() if eventKey in self.__cooldowns else False

    def process(self, eventKey, coolDown=None):
        coolDown = coolDown or DEFAULT_COOLDOWN
        self.__cooldowns[eventKey] = BigWorld.time() + coolDown
