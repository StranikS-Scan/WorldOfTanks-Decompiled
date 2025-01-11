# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/personal_missions_quest_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.personal_missions_quest_info_tooltip_model import PersonalMissionsQuestInfoTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IPersonalMissionsController

class PersonalMissionsQuestInfoTooltip(ViewImpl):
    __slots__ = ('__questId',)
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)

    def __init__(self, questId):
        settings = ViewSettings(R.views.lobby.personal_missions.tooltips.PersonalMissionsQuestInfoTooltip())
        settings.model = PersonalMissionsQuestInfoTooltipModel()
        self.__questId = int(questId)
        super(PersonalMissionsQuestInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsQuestInfoTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsQuestInfoTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            quest = self.__personalMissionsCtrl.getQuest(self.__questId)
            if quest is None:
                return
            vm.setType(quest.getUserAdvice())
        return
