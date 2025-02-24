# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/shared/premature_leave.py
import BigWorld
from BWUtil import AsyncReturn
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from wg_async import wg_await, wg_async
_DIMMER_ALPHA = 0.7

@wg_async
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
    builder.setIcon(R.images.comp7.gui.maps.icons.battle.comp7DeserterLeaveBattle())
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result == DialogButtons.SUBMIT)
