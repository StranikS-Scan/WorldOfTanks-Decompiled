# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/personal_file_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skill_model import TankmanSkillModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skills_group_model import TankmanSkillsGroupModel

class SkillsState(Enum):
    LEARNAVAILABLE = 'available'
    TRAINING = 'training'
    ACHIEVE = 'achieve'
    ZEROSKILLS = 'zeroSkills'
    ALLSKILLS = 'allSkills'


class PersonalFileViewModel(ViewModel):
    __slots__ = ('onIncrease', 'onReset', 'onHoverSkill', 'onLeaveSkill', 'onClickSkill')

    def __init__(self, properties=11, commands=5):
        super(PersonalFileViewModel, self).__init__(properties=properties, commands=commands)

    def getSkillsState(self):
        return SkillsState(self._getString(0))

    def setSkillsState(self, value):
        self._setString(0, value.value)

    def getSelectAvailableSkillsCount(self):
        return self._getNumber(1)

    def setSelectAvailableSkillsCount(self, value):
        self._setNumber(1, value)

    def getIsFemale(self):
        return self._getBool(2)

    def setIsFemale(self, value):
        self._setBool(2, value)

    def getIsTankmanWithDescription(self):
        return self._getBool(3)

    def setIsTankmanWithDescription(self, value):
        self._setBool(3, value)

    def getIsResetDisable(self):
        return self._getBool(4)

    def setIsResetDisable(self, value):
        self._setBool(4, value)

    def getHasIncreaseDiscount(self):
        return self._getBool(5)

    def setHasIncreaseDiscount(self, value):
        self._setBool(5, value)

    def getHasDropSkillDiscount(self):
        return self._getBool(6)

    def setHasDropSkillDiscount(self, value):
        self._setBool(6, value)

    def getIsTankmanInVehicle(self):
        return self._getBool(7)

    def setIsTankmanInVehicle(self, value):
        self._setBool(7, value)

    def getRelevantGroupedSkills(self):
        return self._getArray(8)

    def setRelevantGroupedSkills(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRelevantGroupedSkillsType():
        return TankmanSkillsGroupModel

    def getIrrelevantGroupedSkills(self):
        return self._getArray(9)

    def setIrrelevantGroupedSkills(self, value):
        self._setArray(9, value)

    @staticmethod
    def getIrrelevantGroupedSkillsType():
        return TankmanSkillsGroupModel

    def getCommonSkills(self):
        return self._getArray(10)

    def setCommonSkills(self, value):
        self._setArray(10, value)

    @staticmethod
    def getCommonSkillsType():
        return TankmanSkillModel

    def _initialize(self):
        super(PersonalFileViewModel, self)._initialize()
        self._addStringProperty('skillsState')
        self._addNumberProperty('selectAvailableSkillsCount', 0)
        self._addBoolProperty('isFemale', False)
        self._addBoolProperty('isTankmanWithDescription', False)
        self._addBoolProperty('isResetDisable', False)
        self._addBoolProperty('hasIncreaseDiscount', False)
        self._addBoolProperty('hasDropSkillDiscount', False)
        self._addBoolProperty('isTankmanInVehicle', False)
        self._addArrayProperty('relevantGroupedSkills', Array())
        self._addArrayProperty('irrelevantGroupedSkills', Array())
        self._addArrayProperty('commonSkills', Array())
        self.onIncrease = self._addCommand('onIncrease')
        self.onReset = self._addCommand('onReset')
        self.onHoverSkill = self._addCommand('onHoverSkill')
        self.onLeaveSkill = self._addCommand('onLeaveSkill')
        self.onClickSkill = self._addCommand('onClickSkill')
