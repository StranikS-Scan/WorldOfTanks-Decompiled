# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spam_protection/cooldown_manager.py
import typing
import BigWorld
from gui.battle_control.controllers.spam_protection.spam_constants import DEFAULT_COOLDOWN

class SpamCooldownManager(object):

    def __init__(self):
        self.__cooldowns = {}

    def destroy(self):
        self.__cooldowns.clear()

    def isInProcess(self, eventKey):
        return self.__cooldowns[eventKey] > BigWorld.time() if eventKey in self.__cooldowns else False

    def process(self, eventKey, coolDown=None):
        coolDown = coolDown or DEFAULT_COOLDOWN
        self.__cooldowns[eventKey] = BigWorld.time() + coolDown
