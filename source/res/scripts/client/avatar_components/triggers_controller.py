# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/triggers_controller.py
import logging
import Event
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
_logger = logging.getLogger(__name__)

class TriggersController(object):

    def __init__(self):
        self.__enabled = False
        self.onTrigger = Event.Event()

    def onBecomePlayer(self):
        self.__enabled = True

    def onBecomeNonPlayer(self):
        self.__enabled = False

    def externalTrigger(self, eventId, extra):
        if not self.__enabled:
            return
        self.onTrigger(eventId, extra)

    def fireClientTrigger(self, eventId, isSendToServer):
        if not self.__enabled:
            return
        self.onTrigger(eventId)
        if isSendToServer:
            if self.arena and ARENA_BONUS_TYPE_CAPS.checkAny(self.arena.bonusType, ARENA_BONUS_TYPE_CAPS.TRIGGERS):
                self.cell.externalClientTrigger(eventId)
            else:
                _logger.warning('Failed to trigger event on server. Current arena does not support triggers')

    def handleKey(self, isDown, key, mods):
        pass
