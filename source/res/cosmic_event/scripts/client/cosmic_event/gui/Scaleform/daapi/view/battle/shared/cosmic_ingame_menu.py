# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/battle/shared/cosmic_ingame_menu.py
from BWUtil import AsyncReturn
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.impl.gen import R
from th_async import th_await, th_async

@th_async
def showCosmicLeaverAliveWindow():
    from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow
    quitBattleR = R.strings.dialogs.cosmic
    result = yield th_await(showResDialogWindow(title=quitBattleR.deserter.title(), confirm=quitBattleR.deserter.submit(), cancel=quitBattleR.deserter.cancel(), description=quitBattleR.deserter.message(), icon=R.images.cosmic_event.gui.maps.icons.battle.deserterLeaveBattle()))
    raise AsyncReturn(result)


class CosmicIngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showCosmicLeaverAliveWindow()

    def _getExitResult(self):
        isLeaver = not self.sessionProvider.isReplayPlaying and self.sessionProvider.arenaVisitor.hasFairplay()
        return isLeaver or super(CosmicIngameMenu, self)._getExitResult()
