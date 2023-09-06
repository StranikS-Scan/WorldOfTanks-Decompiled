# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/StoryModeAccountComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents
from helpers import dependency
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import QUEUE_TYPE

class StoryModeAccountComponent(BaseAccountExtensionComponent):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def enqueueBattle(self):
        if not g_playerEvents.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (QUEUE_TYPE.STORY_MODE, self._storyModeCtrl.selectedMissionId))

    def dequeueBattle(self):
        if not g_playerEvents.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, QUEUE_TYPE.STORY_MODE)
