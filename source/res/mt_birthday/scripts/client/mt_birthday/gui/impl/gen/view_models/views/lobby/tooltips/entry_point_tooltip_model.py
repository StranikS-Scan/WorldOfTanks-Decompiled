# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/entry_point_tooltip_model.py
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression import Progression

class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def progression(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionType():
        return Progression

    def getCurrencyCount(self):
        return self._getNumber(1)

    def setCurrencyCount(self, value):
        self._setNumber(1, value)

    def getIsPaused(self):
        return self._getBool(2)

    def setIsPaused(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addViewModelProperty('progression', Progression())
        self._addNumberProperty('currencyCount', 0)
        self._addBoolProperty('isPaused', False)
