# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_widget_level_progress_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NyWidgetLevelProgressModel(NyWithRomanNumbersModel):
    __slots__ = ('onAnimationEnd',)

    def __init__(self, properties=7, commands=1):
        super(NyWidgetLevelProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def hangarName(self):
        return self._getViewModel(1)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

    def getUserLanguage(self):
        return self._getString(2)

    def setUserLanguage(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getMaxLevel(self):
        return self._getNumber(4)

    def setMaxLevel(self, value):
        self._setNumber(4, value)

    def getCurrentPoints(self):
        return self._getNumber(5)

    def setCurrentPoints(self, value):
        self._setNumber(5, value)

    def getMaxPoints(self):
        return self._getNumber(6)

    def setMaxPoints(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NyWidgetLevelProgressModel, self)._initialize()
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self._addStringProperty('userLanguage', '')
        self._addNumberProperty('level', 1)
        self._addNumberProperty('maxLevel', 1)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 1)
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
