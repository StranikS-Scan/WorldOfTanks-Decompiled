# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/user_missions_widget_model.py
from frameworks.wulf import ViewModel

class UserMissionsWidgetModel(ViewModel):
    __slots__ = ('onPresenterDisappear', 'onWidgetUnmounted')

    def __init__(self, properties=3, commands=2):
        super(UserMissionsWidgetModel, self).__init__(properties=properties, commands=commands)

    def getIsBattlePassActive(self):
        return self._getBool(0)

    def setIsBattlePassActive(self, value):
        self._setBool(0, value)

    def getIsAnyEntryPointAvailable(self):
        return self._getBool(1)

    def setIsAnyEntryPointAvailable(self, value):
        self._setBool(1, value)

    def getAreMissionsActive(self):
        return self._getBool(2)

    def setAreMissionsActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(UserMissionsWidgetModel, self)._initialize()
        self._addBoolProperty('isBattlePassActive', False)
        self._addBoolProperty('isAnyEntryPointAvailable', False)
        self._addBoolProperty('areMissionsActive', True)
        self.onPresenterDisappear = self._addCommand('onPresenterDisappear')
        self.onWidgetUnmounted = self._addCommand('onWidgetUnmounted')
