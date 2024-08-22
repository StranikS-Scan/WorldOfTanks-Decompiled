# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/recruit_window/confirm_irrelevant_dialog_model.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.recruit_icon_view_model import RecruitIconViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.tankman_skills_change_base_dialog_model import TankmanSkillsChangeBaseDialogModel

class ConfirmIrrelevantDialogModel(TankmanSkillsChangeBaseDialogModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=2):
        super(ConfirmIrrelevantDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def iconModel(self):
        return self._getViewModel(8)

    @staticmethod
    def getIconModelType():
        return RecruitIconViewModel

    def getName(self):
        return self._getString(9)

    def setName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ConfirmIrrelevantDialogModel, self)._initialize()
        self._addViewModelProperty('iconModel', RecruitIconViewModel())
        self._addStringProperty('name', '')
