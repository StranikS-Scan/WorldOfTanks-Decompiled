# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TournamentsView.py
from typing import TYPE_CHECKING
from gui.Scaleform.daapi.view.lobby import BrowserView
from gui.tournament.sound_constants import TOURNAMENTS_SOUND_SPACE
if TYPE_CHECKING:
    pass

class TournamentsView(BrowserView):
    __background_alpha__ = 1.0
    _COMMON_SOUND_SPACE = TOURNAMENTS_SOUND_SPACE

    def _checkDestroy(self):
        pass
