# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dialog_tankman_model.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_base_model import DialogTankmanBaseModel

class DialogTankmanModel(DialogTankmanBaseModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(DialogTankmanModel, self).__init__(properties=properties, commands=commands)

    def getSkillEfficiency(self):
        return self._getReal(6)

    def setSkillEfficiency(self, value):
        self._setReal(6, value)

    def getFullSkillsCount(self):
        return self._getNumber(7)

    def setFullSkillsCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(DialogTankmanModel, self)._initialize()
        self._addRealProperty('skillEfficiency', 0.0)
        self._addNumberProperty('fullSkillsCount', 0)
