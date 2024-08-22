# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/compare_skills_panel_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.compare_skill_model import CompareSkillModel

class CompareSkillsPanelViewModel(ViewModel):
    __slots__ = ('onClick', 'onReset')

    def __init__(self, properties=1, commands=2):
        super(CompareSkillsPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getSkills(self):
        return self._getArray(0)

    def setSkills(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSkillsType():
        return CompareSkillModel

    def _initialize(self):
        super(CompareSkillsPanelViewModel, self)._initialize()
        self._addArrayProperty('skills', Array())
        self.onClick = self._addCommand('onClick')
        self.onReset = self._addCommand('onReset')
