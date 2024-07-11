# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/shared/races_ingame_menu.py
from BWUtil import AsyncReturn
from wg_async import wg_async, wg_await
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu

@wg_async
def showRAcesLeaverAliveWindow():
    from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow
    quitBattleR = R.strings.dialogs.races
    result = yield wg_await(showResDialogWindow(title=quitBattleR.deserter.title(), confirm=quitBattleR.deserter.submit(), cancel=quitBattleR.deserter.cancel(), description=quitBattleR.deserter.descriptionAlive(), icon=R.images.races.gui.maps.icons.battle.deserterLeaveBattle()))
    raise AsyncReturn(result)


class RacesIngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showRAcesLeaverAliveWindow()

    def _getExitResult(self):
        isLeaver = not self.sessionProvider.isReplayPlaying and self.sessionProvider.arenaVisitor.hasFairplay()
        return isLeaver or super(RacesIngameMenu, self)._getExitResult()
