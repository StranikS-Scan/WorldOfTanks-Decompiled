# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_quest_widget_model.py
from frameworks.wulf import ViewModel

class BootcampQuestWidgetModel(ViewModel):
    __slots__ = ('onQuestClick',)

    def __init__(self, properties=3, commands=1):
        super(BootcampQuestWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrent(self):
        return self._getNumber(0)

    def setCurrent(self, value):
        self._setNumber(0, value)

    def getTotal(self):
        return self._getNumber(1)

    def setTotal(self, value):
        self._setNumber(1, value)

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BootcampQuestWidgetModel, self)._initialize()
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addNumberProperty('tooltipId', 0)
        self.onQuestClick = self._addCommand('onQuestClick')
