# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/battle/premature_leave.py
from BWUtil import AsyncReturn
from wg_async import wg_await, wg_async
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
_DIMMER_ALPHA = 0.7

@wg_async
def showResDialogWindow(title, confirm=None, description=None, icon=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
    builder = ConfirmCancelDialogBuilder()
    builder.setBlur(False)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    builder.setTitle(title)
    builder.setCancelButtonLabel(R.strings.hb_battle.confirmQuit.cancel())
    builder.setConfirmButtonLabel(confirm or R.strings.hb_battle.confirmQuit.confirm())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    if description:
        builder.setDescription(description)
    if icon:
        builder.setIcon(icon, pushingDown=False)
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result == DialogButtons.SUBMIT)


@wg_async
def showLeaverCanRespawnWindow():
    result = yield wg_await(showResDialogWindow(R.strings.hb_battle.confirmQuit.leaver.title(), confirm=R.strings.hb_battle.confirmQuit.leaver.confirm(), description=R.strings.hb_battle.confirmQuit.leaver.descriptionDead(), icon=R.images.historical_battles.gui.maps.icons.confirmView.leaver()))
    raise AsyncReturn(result)


@wg_async
def showLeaverAliveWindow():
    result = yield wg_await(showResDialogWindow(R.strings.hb_battle.confirmQuit.leaver.title(), confirm=R.strings.hb_battle.confirmQuit.leaver.confirm(), description=R.strings.hb_battle.confirmQuit.leaver.descriptionAlive(), icon=R.images.historical_battles.gui.maps.icons.confirmView.leaver()))
    raise AsyncReturn(result)


@wg_async
def showExitWindow():
    result = yield wg_await(showResDialogWindow(R.strings.hb_battle.confirmQuit.title()))
    raise AsyncReturn(result)
