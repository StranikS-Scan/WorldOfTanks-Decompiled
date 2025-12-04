# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/ny_progress_widget_model.py
from frameworks.wulf import ViewModel

class NyProgressWidgetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyProgressWidgetModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getIsPlaceEntrance(self):
        return self._getBool(2)

    def setIsPlaceEntrance(self, value):
        self._setBool(2, value)

    def getRewardsCount(self):
        return self._getNumber(3)

    def setRewardsCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NyProgressWidgetModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('progress', 0)
        self._addBoolProperty('isPlaceEntrance', False)
        self._addNumberProperty('rewardsCount', 0)
