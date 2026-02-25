# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TournamentsView.py
from typing import TYPE_CHECKING
from gui.Scaleform.daapi.view.lobby import BrowserView
from gui.tournament.sound_constants import TOURNAMENTS_SOUND_SPACE
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if TYPE_CHECKING:
    pass

class TournamentsView(BrowserView):
    __eventsCache = dependency.descriptor(IEventsCache)
    __background_alpha__ = 1.0
    _BROWSER_SOUND_SPACE = TOURNAMENTS_SOUND_SPACE

    def _checkDestroy(self):
        pass

    def _populate(self):
        super(TournamentsView, self)._populate()
        self.__eventsCache.onTournamentsVisited()
