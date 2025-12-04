# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_selfRank_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_player_model import NyPlayerModel

class NySelfrankModel(NyPlayerModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NySelfrankModel, self).__init__(properties=properties, commands=commands)

    def getOwnSpaID(self):
        return self._getNumber(5)

    def setOwnSpaID(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NySelfrankModel, self)._initialize()
        self._addNumberProperty('ownSpaID', 0)
