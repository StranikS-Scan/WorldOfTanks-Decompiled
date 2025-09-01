# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/battle/shared/premature_leave.py
from BWUtil import AsyncReturn
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from wg_async import wg_await, wg_async
_DIMMER_ALPHA = 0.7

@wg_async
def showComp7LightLeaverAliveWindow():
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.gf_builders import ConfirmCancelDescriptionDialogBuilder
    builder = ConfirmCancelDescriptionDialogBuilder()
    builder.setBlur(False)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    builder.setTitle(R.strings.dialogs.comp7_light.deserter.title())
    builder.setCancelButtonLabel(R.strings.dialogs.comp7_light.deserter.cancel())
    builder.setConfirmButtonLabel(R.strings.dialogs.comp7_light.deserter.submit())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    builder.setDescriptionMsg(R.strings.dialogs.comp7_light.deserter.message())
    builder.setIcon(R.images.comp7_core.gui.maps.icons.battle.comp7DeserterLeaveBattle())
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result == DialogButtons.SUBMIT)
