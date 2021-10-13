# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/yha/yha_entry_point_model.py
from frameworks.wulf import ViewModel

class YhaEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=2, commands=1):
        super(YhaEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getDueDate(self):
        return self._getString(0)

    def setDueDate(self, value):
        self._setString(0, value)

    def getIsSmall(self):
        return self._getBool(1)

    def setIsSmall(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(YhaEntryPointModel, self)._initialize()
        self._addStringProperty('dueDate', '')
        self._addBoolProperty('isSmall', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
