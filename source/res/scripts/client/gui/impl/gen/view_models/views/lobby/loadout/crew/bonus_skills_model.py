# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/bonus_skills_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.perk_model import PerkModel

class BonusSkillsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BonusSkillsModel, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(0)

    def setRole(self, value):
        self._setString(0, value)

    def getNewCount(self):
        return self._getNumber(1)

    def setNewCount(self, value):
        self._setNumber(1, value)

    def getTrainingProgress(self):
        return self._getNumber(2)

    def setTrainingProgress(self, value):
        self._setNumber(2, value)

    def getSkills(self):
        return self._getArray(3)

    def setSkills(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSkillsType():
        return PerkModel

    def _initialize(self):
        super(BonusSkillsModel, self)._initialize()
        self._addStringProperty('role', '')
        self._addNumberProperty('newCount', 0)
        self._addNumberProperty('trainingProgress', -1)
        self._addArrayProperty('skills', Array())
