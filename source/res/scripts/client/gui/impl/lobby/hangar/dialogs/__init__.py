# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/dialogs/__init__.py
from __future__ import absolute_import
from BWUtil import AsyncReturn
from gui.impl.dialogs import dialogs
from gui.impl.lobby.dialogs.full_screen_param_dialog_view import FullScreenParamDialogView
from wg_async import wg_async, wg_await

@wg_async
def showTypeParamConfirmDialog(layoutID, dialogType, dialogParams, wrappedViewClass=None):
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=layoutID, wrappedViewClass=wrappedViewClass or FullScreenParamDialogView, dialogLayoutID=layoutID, dialogType=dialogType, dialogParams=dialogParams))
    if result.busy:
        raise AsyncReturn((False, {}))
    raise AsyncReturn(result.result)
