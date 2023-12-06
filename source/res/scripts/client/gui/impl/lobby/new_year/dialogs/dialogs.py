# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/dialogs.py
from wg_async import wg_async, wg_await
from BWUtil import AsyncReturn
from gui.impl.dialogs import dialogs

@wg_async
def showBuyDialog(window):
    result = yield wg_await(dialogs.show(window))
    raise AsyncReturn(result)
