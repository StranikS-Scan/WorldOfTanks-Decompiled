# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_widget_entry_point_view_model.py
from frameworks.wulf import ViewModel

class EarlyAccessWidgetEntryPointViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=5, commands=1):
        super(EarlyAccessWidgetEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getStartTime(self):
        return self._getNumber(1)

    def setStartTime(self, value):
        self._setNumber(1, value)

    def getEndTime(self):
        return self._getNumber(2)

    def setEndTime(self, value):
        self._setNumber(2, value)

    def getCurrentTime(self):
        return self._getNumber(3)

    def setCurrentTime(self, value):
        self._setNumber(3, value)

    def getIsRewardAvailable(self):
        return self._getBool(4)

    def setIsRewardAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(EarlyAccessWidgetEntryPointViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('endTime', 0)
        self._addNumberProperty('currentTime', 0)
        self._addBoolProperty('isRewardAvailable', False)
        self.onAction = self._addCommand('onAction')
