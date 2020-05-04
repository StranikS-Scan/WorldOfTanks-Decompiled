# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/general_progress_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_skill_model import CharacteristicsSkillModel
from gui.impl.gen.view_models.views.lobby.secret_event.tank_model import TankModel

class GeneralProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(GeneralProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def prizeTank(self):
        return self._getViewModel(0)

    @property
    def abilities(self):
        return self._getViewModel(1)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getResource(3)

    def setName(self, value):
        self._setResource(3, value)

    def getDescription(self):
        return self._getResource(4)

    def setDescription(self, value):
        self._setResource(4, value)

    def getProgress(self):
        return self._getNumber(5)

    def setProgress(self, value):
        self._setNumber(5, value)

    def getProgressMax(self):
        return self._getNumber(6)

    def setProgressMax(self, value):
        self._setNumber(6, value)

    def getLevel(self):
        return self._getNumber(7)

    def setLevel(self, value):
        self._setNumber(7, value)

    def getIsComplete(self):
        return self._getBool(8)

    def setIsComplete(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(GeneralProgressModel, self)._initialize()
        self._addViewModelProperty('prizeTank', TankModel())
        self._addViewModelProperty('abilities', UserListModel())
        self._addNumberProperty('id', 0)
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('progressMax', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isComplete', False)
