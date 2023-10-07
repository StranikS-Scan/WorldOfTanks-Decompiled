# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWAccountComponent.py
import logging
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
import halloween_account_commands as hac
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
_logger = logging.getLogger(__name__)

class HWAccountComponent(BaseAccountExtensionComponent):
    _hwController = dependency.descriptor(IHalloweenController)

    def applyDailyQuest(self, phase, callback=None):
        _logger.debug('apply daily quest')
        self.entity._doCmdInt(hac.CMD_HW_APPLY_DAILY_QUEST, phase, callback)

    def enqueueBattle(self, vehInvID, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, [queueType, vehInvID])

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)
