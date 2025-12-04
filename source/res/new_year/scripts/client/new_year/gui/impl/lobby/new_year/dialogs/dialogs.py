# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/dialogs/dialogs.py
from th_async import th_async, th_await
from BWUtil import AsyncReturn
from gui.impl.dialogs import dialogs

@th_async
def showBuyDialog(window):
    result = yield th_await(dialogs.show(window))
    raise AsyncReturn(result)
