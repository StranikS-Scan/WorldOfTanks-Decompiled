# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tournament_banner_view_model.py
from gui.impl.gen.view_models.views.battle_royale.tournament_banner_base_view_model import TournamentBannerBaseViewModel

class TournamentBannerViewModel(TournamentBannerBaseViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(TournamentBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getIsExtended(self):
        return self._getBool(3)

    def setIsExtended(self, value):
        self._setBool(3, value)

    def getImprovedGraphics(self):
        return self._getBool(4)

    def setImprovedGraphics(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(TournamentBannerViewModel, self)._initialize()
        self._addBoolProperty('isExtended', False)
        self._addBoolProperty('improvedGraphics', False)
        self.onClick = self._addCommand('onClick')
