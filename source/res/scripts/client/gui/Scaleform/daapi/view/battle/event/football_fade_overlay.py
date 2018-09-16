# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_fade_overlay.py
from gui.battle_control.controllers.football_ctrl import IFootballView
from gui.Scaleform.daapi.view.meta.FootballFadeOverlayMeta import FootballFadeOverlayMeta

class FootballFadeOverlay(FootballFadeOverlayMeta, IFootballView):

    def onFootballFadeOut(self, canFade, delay):
        self.as_setFadeS(canFade, delay)

    def onWinnerDeclared(self, winner, delay):
        if winner is not None:
            self.as_setFadeS(False, delay)
        return
