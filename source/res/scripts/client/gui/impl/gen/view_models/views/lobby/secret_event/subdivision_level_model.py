# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/subdivision_level_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_skill_model import CharacteristicsSkillModel

class SubdivisionLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SubdivisionLevelModel, self).__init__(properties=properties, commands=commands)

    @property
    def abilities(self):
        return self._getViewModel(0)

    def getTankIcon(self):
        return self._getResource(1)

    def setTankIcon(self, value):
        self._setResource(1, value)

    def getTankId(self):
        return self._getNumber(2)

    def setTankId(self, value):
        self._setNumber(2, value)

    def getIsComplete(self):
        return self._getBool(3)

    def setIsComplete(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SubdivisionLevelModel, self)._initialize()
        self._addViewModelProperty('abilities', UserListModel())
        self._addResourceProperty('tankIcon', R.invalid())
        self._addNumberProperty('tankId', 0)
        self._addBoolProperty('isComplete', False)
