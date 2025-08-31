# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/premature_leave.py
import BigWorld
from BWUtil import AsyncReturn
from constants import ARENA_GUI_TYPE
from gui.impl.dialogs.dialog_template_utils import closeDialogTemplate
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from th_async import th_await, th_async
_DIMMER_ALPHA = 0.7
_PREMATURE_LEAVE_DIALOG_ID = 'PREMATURE_LEAVE_DIALOG'

def closeDialogWindow():
    closeDialogTemplate(_PREMATURE_LEAVE_DIALOG_ID)


@th_async
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
    result = yield th_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result)


@th_async
def showResDialogWindow(title, confirm=None, cancel=None, description=None, icon=None):
    result = yield th_await(showDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result == DialogButtons.SUBMIT)


@th_async
def showCancellationDialogWindow(title, confirm=None, cancel=None, description=None, icon=None):
    result = yield th_await(showDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result == DialogButtons.CANCEL)


@th_async
def showLeaverAliveWindow(IGR=False):
    quitBattleR = R.strings.dialogs.quitBattle
    title = quitBattleR.IGR.leaver.title() if IGR else quitBattleR.leaver.title()
    confirm = quitBattleR.IGR.leaver.submit() if IGR else quitBattleR.leaver.submit()
    cancel = quitBattleR.IGR.leaver.cancel() if IGR else quitBattleR.leaver.cancel()
    description = quitBattleR.IGR.leaver.descriptionAlive() if IGR else quitBattleR.leaver.descriptionAlive()
    icon = R.images.gui.maps.icons.battle.deserterLeaveBattle()
    result = yield th_await(showResDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result)


@th_async
def showComp7LeaverAliveWindow():
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.gf_builders import ConfirmCancelWarningDialogBuilder, ConfirmCancelDescriptionDialogBuilder
    arenaGuiType = BigWorld.player().arenaGuiType
    if arenaGuiType == ARENA_GUI_TYPE.COMP7:
        builder = ConfirmCancelWarningDialogBuilder()
        builder.setWarningMsg(R.strings.dialogs.comp7.deserter.msgTitle())
    else:
        builder = ConfirmCancelDescriptionDialogBuilder()
    builder.setBlur(False)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    builder.setTitle(R.strings.dialogs.comp7.deserter.title())
    builder.setCancelButtonLabel(R.strings.dialogs.comp7.deserter.cancel())
    builder.setConfirmButtonLabel(R.strings.dialogs.comp7.deserter.submit())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    builder.setDescriptionMsg(R.strings.dialogs.comp7.deserter.message())
    if arenaGuiType == ARENA_GUI_TYPE.COMP7:
        builder.setWarningMsg(R.strings.dialogs.comp7.deserter.msgTitle())
    builder.setIcon(R.images.comp7.gui.maps.icons.comp7.battle.comp7DeserterLeaveBattle())
    result = yield th_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result == DialogButtons.SUBMIT)


@th_async
def showWhiteTigerLeaverAliveWindow():
    title = R.strings.dialogs.white_tiger.deserter.title
    confirm = R.strings.dialogs.white_tiger.deserter.submit()
    cancel = R.strings.dialogs.white_tiger.deserter.cancel()
    description = R.strings.dialogs.white_tiger.deserter.message()
    icon = R.images.gui.maps.icons.battle.deserterLeaveBattle()
    result = yield th_await(showResDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result)


@th_async
def showLeaverReplayWindow():
    result = yield th_await(showResDialogWindow(R.strings.dialogs.quitBattle.replay.title(), confirm=R.strings.dialogs.quitBattle.replay.submit(), cancel=R.strings.dialogs.quitBattle.replay.cancel()))
    raise AsyncReturn(result)


@th_async
def showExitWindow():
    result = yield th_await(showResDialogWindow(R.strings.dialogs.quitBattle.title()))
    raise AsyncReturn(result)
