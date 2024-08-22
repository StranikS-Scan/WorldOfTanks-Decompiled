# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/tankman_skills_change_base_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_with_skills_model import DialogTankmanWithSkillsModel

class TankmanSkillsChangeBaseDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=2):
        super(TankmanSkillsChangeBaseDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanBefore(self):
        return self._getViewModel(6)

    @staticmethod
    def getTankmanBeforeType():
        return DialogTankmanWithSkillsModel

    @property
    def tankmanAfter(self):
        return self._getViewModel(7)

    @staticmethod
    def getTankmanAfterType():
        return DialogTankmanWithSkillsModel

    def _initialize(self):
        super(TankmanSkillsChangeBaseDialogModel, self)._initialize()
        self._addViewModelProperty('tankmanBefore', DialogTankmanWithSkillsModel())
        self._addViewModelProperty('tankmanAfter', DialogTankmanWithSkillsModel())
