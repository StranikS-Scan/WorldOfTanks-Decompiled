# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: newbie_start_page/scripts/client/newbie_start_page/gui/impl/gen/view_models/views/lobby/newbie_start_page/newbie_start_page_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ExperienceChoice(IntEnum):
    UNSPECIFIED = 0
    NEWBIE = 1
    INEXPERIENCED = 2
    EXPERIENCED = 3
    SKIPPED = 4


class NewbieStartPageViewModel(ViewModel):
    __slots__ = ('onSelect',)
    ON_SELECT_ARG_NAME = 'level'

    def __init__(self, properties=1, commands=1):
        super(NewbieStartPageViewModel, self).__init__(properties=properties, commands=commands)

    def getLevels(self):
        return self._getArray(0)

    def setLevels(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLevelsType():
        return ExperienceChoice

    def _initialize(self):
        super(NewbieStartPageViewModel, self)._initialize()
        self._addArrayProperty('levels', Array())
        self.onSelect = self._addCommand('onSelect')
