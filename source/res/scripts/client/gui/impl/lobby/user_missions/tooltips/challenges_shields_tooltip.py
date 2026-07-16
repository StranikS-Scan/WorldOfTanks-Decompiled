# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/challenges_shields_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.tooltips.challenges_shields_tooltip_model import ChallengesShieldsTooltipModel
from gui.impl.pub import ViewImpl

class ChallengesShieldsTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.challenges_shields_tooltip())
        settings.model = ChallengesShieldsTooltipModel()
        super(ChallengesShieldsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChallengesShieldsTooltip, self).getViewModel()
