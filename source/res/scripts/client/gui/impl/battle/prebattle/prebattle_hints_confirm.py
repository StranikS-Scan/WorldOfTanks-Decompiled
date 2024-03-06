# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle/prebattle_hints_confirm.py
from helpers import dependency
from skeletons.gui.prebattle_hints.newbie_controller import INewbiePrebattleHintsController
from wg_async import wg_async, wg_await
from gui.impl.gen import R
from gui.impl.dialogs import dialogs
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.dialogs.dialog_template_button import ConfirmButton

@wg_async
def showPrebattleHintsConfirm():
    builder = ResDialogBuilder()
    res = R.strings.prebattle.hints.confirmDialog
    builder.setTitle(res.title())
    builder.setDescription(res.message())
    builder.setIcon(R.images.gui.maps.icons.battleLoading.hints.confirm())
    builder.addButton(ConfirmButton(res.confirm()))
    builder.setFocusedButtonID(DialogButtons.SUBMIT)
    yield wg_await(dialogs.show(builder.build()))
    dependency.instance(INewbiePrebattleHintsController).onConfirmationWindowShown()
