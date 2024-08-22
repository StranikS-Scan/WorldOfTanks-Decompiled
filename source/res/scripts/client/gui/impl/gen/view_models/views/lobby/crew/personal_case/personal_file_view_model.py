# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/personal_file_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.tankman_info_model import TankmanInfoModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.post_progression_widget_model import PostProgressionWidgetModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.skills_matrix_model import SkillsMatrixModel

class PersonalFileViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(PersonalFileViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getTankmanInfoType():
        return TankmanInfoModel

    @property
    def skills(self):
        return self._getViewModel(1)

    @staticmethod
    def getSkillsType():
        return SkillsMatrixModel

    @property
    def postProgression(self):
        return self._getViewModel(2)

    @staticmethod
    def getPostProgressionType():
        return PostProgressionWidgetModel

    def getTankmanId(self):
        return self._getNumber(3)

    def setTankmanId(self, value):
        self._setNumber(3, value)

    def getSkillsEfficiency(self):
        return self._getReal(4)

    def setSkillsEfficiency(self, value):
        self._setReal(4, value)

    def getIsTankmanInVehicle(self):
        return self._getBool(5)

    def setIsTankmanInVehicle(self, value):
        self._setBool(5, value)

    def getHasPostProgression(self):
        return self._getBool(6)

    def setHasPostProgression(self, value):
        self._setBool(6, value)

    def getIsPostProgressionAnimated(self):
        return self._getBool(7)

    def setIsPostProgressionAnimated(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(PersonalFileViewModel, self)._initialize()
        self._addViewModelProperty('tankmanInfo', TankmanInfoModel())
        self._addViewModelProperty('skills', SkillsMatrixModel())
        self._addViewModelProperty('postProgression', PostProgressionWidgetModel())
        self._addNumberProperty('tankmanId', 0)
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addBoolProperty('isTankmanInVehicle', False)
        self._addBoolProperty('hasPostProgression', False)
        self._addBoolProperty('isPostProgressionAnimated', False)
