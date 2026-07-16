# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/challenges_missions_progress_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.challenge_quest_progress_model import ChallengeQuestProgressModel

class ChallengesMissionsProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/post_battle/challenges_quests/challenges_quests.js'

    def __init__(self, properties=1, commands=1):
        super(ChallengesMissionsProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def challengeQuest(self):
        return self._getViewModel(0)

    @staticmethod
    def getChallengeQuestType():
        return ChallengeQuestProgressModel

    def _initialize(self):
        super(ChallengesMissionsProgressModel, self)._initialize()
        self._addViewModelProperty('challengeQuest', ChallengeQuestProgressModel())
        self.onNavigate = self._addCommand('onNavigate')
