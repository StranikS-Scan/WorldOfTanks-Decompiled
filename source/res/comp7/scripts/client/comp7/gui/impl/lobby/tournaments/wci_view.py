# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tournaments/wci_view.py
from comp7.gui.impl.gen.view_models.views.lobby.tournaments.match_model import MatchStage
from comp7.gui.impl.lobby.tournaments.tournament_view import TournamentView
from helpers.ingame_tournament_helper import IngameTournamentType
from gui.impl.gen import R

class WciView(TournamentView):
    _TOURNAMENT_TYPE = IngameTournamentType.WCI
    _TOURNAMENT_VIEW = R.views.comp7.mono.lobby.tournaments.wci_view()
    _MATCH_ROUND_TO_MATCH_STAGE = {2: MatchStage.UBSEMIFINALS,
     1: MatchStage.UBFINALS,
     0: MatchStage.GRANDFINALS,
     -4: MatchStage.LBROUND1,
     -3: MatchStage.LBROUND2,
     -2: MatchStage.LBSEMIFINALS,
     -1: MatchStage.LBFINALS}
