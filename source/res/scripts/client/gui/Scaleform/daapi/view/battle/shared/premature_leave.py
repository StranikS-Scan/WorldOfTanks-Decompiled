# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/premature_leave.py
import BigWorld
from BWUtil import AsyncReturn
from constants import ARENA_GUI_TYPE
from gui.impl.dialogs.dialog_template_utils import closeDialogTemplate
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from wg_async import wg_await, wg_async
_DIMMER_ALPHA = 0.7
_PREMATURE_LEAVE_DIALOG_ID = 'PREMATURE_LEAVE_DIALOG'

def closeDialogWindow():
    closeDialogTemplate(_PREMATURE_LEAVE_DIALOG_ID)


@wg_async
def showDialogWindow(title, confirm=None, cancel=None, description=None, icon=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
    builder = ConfirmCancelDialogBuilder(uniqueID=_PREMATURE_LEAVE_DIALOG_ID)
    builder.setBlur(False)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    builder.setTitle(title)
    builder.setCancelButtonLabel(cancel or R.strings.dialogs.quitBattle.cancel())
    builder.setConfirmButtonLabel(confirm or R.strings.dialogs.quitBattle.submit())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    if description:
        builder.setDescription(description)
    if icon:
        builder.setIcon(icon)
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result)


@wg_async
def showResDialogWindow(title, confirm=None, cancel=None, description=None, icon=None):
    result = yield wg_await(showDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result == DialogButtons.SUBMIT)


@wg_async
def showCancellationDialogWindow(title, confirm=None, cancel=None, description=None, icon=None):
    result = yield wg_await(showDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result == DialogButtons.CANCEL)


@wg_async
def showLeaverAliveWindow(IGR=False):
    quitBattleR = R.strings.dialogs.quitBattle
    title = quitBattleR.IGR.leaver.title() if IGR else quitBattleR.leaver.title()
    confirm = quitBattleR.IGR.leaver.submit() if IGR else quitBattleR.leaver.submit()
    cancel = quitBattleR.IGR.leaver.cancel() if IGR else quitBattleR.leaver.cancel()
    description = quitBattleR.IGR.leaver.descriptionAlive() if IGR else quitBattleR.leaver.descriptionAlive()
    icon = R.images.gui.maps.icons.battle.deserterLeaveBattle()
    result = yield wg_await(showResDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result)


@wg_async
def showComp7LeaverAliveWindow():
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder, ConfirmCancelDescriptionDialogBuilder
    arenaGuiType = BigWorld.player().arenaGuiType
    if arenaGuiType == ARENA_GUI_TYPE.COMP7:
        builder = ConfirmCancelDialogBuilder()
        builder.setDescription(R.strings.dialogs.comp7.deserter.message())
    else:
        builder = ConfirmCancelDescriptionDialogBuilder()
        builder.setDescriptionMsg(R.strings.dialogs.comp7.deserter.message())
    builder.setBlur(False)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    builder.setTitle(R.strings.dialogs.comp7.deserter.title())
    builder.setCancelButtonLabel(R.strings.dialogs.comp7.deserter.cancel())
    builder.setConfirmButtonLabel(R.strings.dialogs.comp7.deserter.submit())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    builder.setIcon(R.images.gui.maps.icons.comp7.battle.comp7DeserterLeaveBattle())
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result == DialogButtons.SUBMIT)


@wg_async
def showLeaverReplayWindow():
    result = yield wg_await(showResDialogWindow(R.strings.dialogs.quitBattle.replay.title(), confirm=R.strings.dialogs.quitBattle.replay.submit(), cancel=R.strings.dialogs.quitBattle.replay.cancel()))
    raise AsyncReturn(result)


@wg_async
def showExitWindow():
    result = yield wg_await(showResDialogWindow(R.strings.dialogs.quitBattle.title()))
    raise AsyncReturn(result)
