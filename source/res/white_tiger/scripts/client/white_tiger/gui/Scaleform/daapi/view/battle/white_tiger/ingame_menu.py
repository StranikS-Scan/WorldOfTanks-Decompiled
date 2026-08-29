# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/ingame_menu.py
from gui.impl.gen import R
from th_async import th_await, th_async
from BWUtil import AsyncReturn
from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu

@th_async
def showWhiteTigerLeaverAliveWindow():
    title = R.strings.dialogs.white_tiger.deserter.title
    confirm = R.strings.dialogs.white_tiger.deserter.submit()
    cancel = R.strings.dialogs.white_tiger.deserter.cancel()
    description = R.strings.dialogs.white_tiger.deserter.message()
    icon = R.images.gui.maps.icons.battle.deserterLeaveBattle()
    result = yield th_await(showResDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result)


class WTIngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showWhiteTigerLeaverAliveWindow()
