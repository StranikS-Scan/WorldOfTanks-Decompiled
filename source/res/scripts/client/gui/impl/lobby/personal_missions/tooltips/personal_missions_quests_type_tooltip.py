# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/personal_missions_quests_type_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.personal_missions_quests_type_tooltip_model import PersonalMissionsQuestsTypeTooltipModel
from gui.impl.pub import ViewImpl

class PersonalMissionsQuestsTypeTooltip(ViewImpl):

    def __init__(self, type):
        settings = ViewSettings(R.views.lobby.personal_missions.tooltips.PersonalMissionsQuestsTypeTooltip())
        settings.model = PersonalMissionsQuestsTypeTooltipModel()
        settings.args = (type,)
        super(PersonalMissionsQuestsTypeTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsQuestsTypeTooltip, self).getViewModel()

    def _onLoading(self, type, *args, **kwargs):
        super(PersonalMissionsQuestsTypeTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setQuestType(type)
