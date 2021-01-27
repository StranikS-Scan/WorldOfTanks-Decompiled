# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_team_rewards_view_model.py
from gui.impl.gen.view_models.views.lobby.bob.bob_common_rewards_view_model import BobCommonRewardsViewModel

class BobTeamRewardsViewModel(BobCommonRewardsViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BobTeamRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BobTeamRewardsViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
