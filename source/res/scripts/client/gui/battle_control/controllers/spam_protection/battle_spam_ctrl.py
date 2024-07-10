# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spam_protection/battle_spam_ctrl.py
import typing
from gui.battle_control.arena_info.interfaces import IBattleSpamController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.spam_protection.cooldown_manager import SpamCooldownManager
from gui.battle_control.controllers.spam_protection.spam_constants import SpamEvents, SPAM_COOLDOWNS

class BattleSpamController(IBattleSpamController):

    def __init__(self):
        self.__cooldown = SpamCooldownManager()

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__cooldown.destroy()

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_SPAM_CTRL

    def filterAllyHitMessage(self, targetID):
        return self.__filterEvent(SpamEvents.ALLY_HIT_MESSAGE, (SpamEvents.ALLY_HIT_MESSAGE, targetID))

    def filterAutoShootTracerSound(self, attackerID):
        return self.__filterEvent(SpamEvents.AUTO_SHOOT_TRACER_SOUND, (SpamEvents.AUTO_SHOOT_TRACER_SOUND, attackerID), adjustCooldown=False)

    def filterFullscreenEffects(self, attackerID):
        return self.__filterEvent(SpamEvents.FULLSCREEN_EFFECT, (SpamEvents.FULLSCREEN_EFFECT, attackerID))

    def filterMarkersHitState(self, targetID, stateKey):
        return self.__filterEvent(SpamEvents.MARKERS_HIT_STATE, (SpamEvents.MARKERS_HIT_STATE, targetID, stateKey))

    def __filterEvent(self, eventID, eventKey=None, adjustCooldown=True):
        eventKey = eventKey or eventID
        isEventCooldown = self.__cooldown.isInProcess(eventKey)
        if not isEventCooldown or adjustCooldown:
            self.__cooldown.process(eventKey, SPAM_COOLDOWNS.get(eventID))
        return not isEventCooldown
