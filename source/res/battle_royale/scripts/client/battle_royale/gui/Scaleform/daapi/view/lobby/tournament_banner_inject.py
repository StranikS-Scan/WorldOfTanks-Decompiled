# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tournament_banner_inject.py
from battle_royale.gui.impl.lobby.views.tournament_banner_view import TournamentBannerView
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.EventTournamentBannerInjectMeta import EventTournamentBannerInjectMeta
from shared_utils import nextTick

class TournamentBannerComponent(EventTournamentBannerInjectMeta):
    __slots__ = ('__view', '__isExtended')

    def __init__(self):
        super(TournamentBannerComponent, self).__init__()
        self.__view = None
        self.__isExtended = False
        return

    def setIsExtended(self, value):
        self.__isExtended = value
        if self.__view is not None:
            self.__view.setIsExtended(self.__isExtended)
        return

    def _onPopulate(self):
        self.__createInject()

    def _dispose(self):
        self.__view = None
        super(TournamentBannerComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = TournamentBannerView(isExtended=self.__isExtended, flags=ViewFlags.VIEW)
        return self.__view

    @nextTick
    def __createInject(self):
        self._createInjectView()
