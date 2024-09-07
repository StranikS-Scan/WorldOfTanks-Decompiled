# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/winback_widget_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class WinbackState(Enum):
    IN_PROGRESS = 'inProgress'
    COMPLETE = 'complete'
    DISABLE = 'disable'
    LAST_STAGE = 'lastStage'


class WinbackWidgetViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(WinbackWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return WinbackState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getSelectableRewardsCount(self):
        return self._getNumber(2)

    def setSelectableRewardsCount(self, value):
        self._setNumber(2, value)

    def getProgressionName(self):
        return self._getString(3)

    def setProgressionName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(WinbackWidgetViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('selectableRewardsCount', 0)
        self._addStringProperty('progressionName', '')
        self.onClick = self._addCommand('onClick')
