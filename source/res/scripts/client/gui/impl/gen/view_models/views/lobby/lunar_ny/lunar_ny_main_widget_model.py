# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/lunar_ny_main_widget_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.bonuses_model import BonusesModel

class LunarNyMainWidgetModel(ViewModel):
    __slots__ = ('onWidgetClick', 'onEnvelopeClick')

    def __init__(self, properties=4, commands=2):
        super(LunarNyMainWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    def getNewCount(self):
        return self._getNumber(1)

    def setNewCount(self, value):
        self._setNumber(1, value)

    def getCurrentProgressionLevel(self):
        return self._getNumber(2)

    def setCurrentProgressionLevel(self, value):
        self._setNumber(2, value)

    def getBonusesSupported(self):
        return self._getBool(3)

    def setBonusesSupported(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(LunarNyMainWidgetModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addNumberProperty('newCount', 0)
        self._addNumberProperty('currentProgressionLevel', 0)
        self._addBoolProperty('bonusesSupported', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
        self.onEnvelopeClick = self._addCommand('onEnvelopeClick')
