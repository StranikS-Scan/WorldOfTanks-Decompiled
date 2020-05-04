# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/subdivision_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.secret_event.subdivision_level_model import SubdivisionLevelModel

class SubdivisionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(SubdivisionModel, self).__init__(properties=properties, commands=commands)

    @property
    def level1(self):
        return self._getViewModel(0)

    @property
    def level2(self):
        return self._getViewModel(1)

    @property
    def level3(self):
        return self._getViewModel(2)

    def getId(self):
        return self._getNumber(3)

    def setId(self, value):
        self._setNumber(3, value)

    def getLogo(self):
        return self._getResource(4)

    def setLogo(self, value):
        self._setResource(4, value)

    def getLabel(self):
        return self._getResource(5)

    def setLabel(self, value):
        self._setResource(5, value)

    def getMaxProgress(self):
        return self._getNumber(6)

    def setMaxProgress(self, value):
        self._setNumber(6, value)

    def getCurrentProgress(self):
        return self._getNumber(7)

    def setCurrentProgress(self, value):
        self._setNumber(7, value)

    def getIsDone(self):
        return self._getBool(8)

    def setIsDone(self, value):
        self._setBool(8, value)

    def getIsSelected(self):
        return self._getBool(9)

    def setIsSelected(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(SubdivisionModel, self)._initialize()
        self._addViewModelProperty('level1', SubdivisionLevelModel())
        self._addViewModelProperty('level2', SubdivisionLevelModel())
        self._addViewModelProperty('level3', SubdivisionLevelModel())
        self._addNumberProperty('id', 0)
        self._addResourceProperty('logo', R.invalid())
        self._addResourceProperty('label', R.invalid())
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('currentProgress', 0)
        self._addBoolProperty('isDone', False)
        self._addBoolProperty('isSelected', False)
