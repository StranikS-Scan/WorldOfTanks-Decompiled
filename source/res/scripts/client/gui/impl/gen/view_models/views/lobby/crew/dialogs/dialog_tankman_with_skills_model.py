# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dialog_tankman_with_skills_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_base_model import DialogTankmanBaseModel

class DialogTankmanWithSkillsModel(DialogTankmanBaseModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(DialogTankmanWithSkillsModel, self).__init__(properties=properties, commands=commands)

    @property
    def skillList(self):
        return self._getViewModel(6)

    @staticmethod
    def getSkillListType():
        return CrewSkillListModel

    def _initialize(self):
        super(DialogTankmanWithSkillsModel, self)._initialize()
        self._addViewModelProperty('skillList', CrewSkillListModel())
