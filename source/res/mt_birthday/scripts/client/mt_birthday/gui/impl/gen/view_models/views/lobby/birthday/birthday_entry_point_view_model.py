# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/birthday_entry_point_view_model.py
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression import Progression
from gui.impl.gen.view_models.views.lobby.hangar.header_widget_view_model import HeaderWidgetViewModel

class BirthdayEntryPointViewModel(HeaderWidgetViewModel):
    __slots__ = ('onClick', 'onAnimationEnded', 'onComponentDestroyed')

    def __init__(self, properties=3, commands=4):
        super(BirthdayEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progression(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionType():
        return Progression

    def getIsPaused(self):
        return self._getBool(1)

    def setIsPaused(self, value):
        self._setBool(1, value)

    def getEconomicBonus(self):
        return self._getNumber(2)

    def setEconomicBonus(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BirthdayEntryPointViewModel, self)._initialize()
        self._addViewModelProperty('progression', Progression())
        self._addBoolProperty('isPaused', False)
        self._addNumberProperty('economicBonus', 0)
        self.onClick = self._addCommand('onClick')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')
        self.onComponentDestroyed = self._addCommand('onComponentDestroyed')
