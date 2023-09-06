# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/prb_control/entities/pre_queue/__init__.py
from adisp import adisp_process, adisp_async
import wg_async as future_async
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import WarningDialogBuilder
from gui.impl.gen import R
from helpers import dependency
from story_mode.skeletons.story_mode_controller import IStoryModeController

@adisp_async
@future_async.wg_async
def checkMissionCompleted(callback):
    ctrl = dependency.instance(IStoryModeController)
    if ctrl.isMissionCompleted(ctrl.selectedMissionId):
        builder = WarningDialogBuilder()
        rMsg = R.strings.sm_lobby.dialogs.missionCompleted
        builder.setMessagesAndButtons(rMsg, rMsg)
        builder.setShowBalance(True)
        success = yield future_async.wg_await(dialogs.showSimple(builder.buildInLobby()))
        callback(success)
    else:
        callback(True)


def missionCompletionCheck(func):

    @adisp_process
    def wrapper(*args, **kwargs):
        res = yield checkMissionCompleted()
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper
