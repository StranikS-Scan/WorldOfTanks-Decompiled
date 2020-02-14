# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/epic/quest_progress_item_model.py
from frameworks.wulf import ViewModel

class QuestProgressItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(QuestProgressItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getEventType(self):
        return self._getNumber(1)

    def setEventType(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getDesc(self):
        return self._getString(3)

    def setDesc(self, value):
        self._setString(3, value)

    def getRewards(self):
        return self._getString(4)

    def setRewards(self, value):
        self._setString(4, value)

    def getValue(self):
        return self._getNumber(5)

    def setValue(self, value):
        self._setNumber(5, value)

    def getDeltaLabel(self):
        return self._getString(6)

    def setDeltaLabel(self, value):
        self._setString(6, value)

    def getMaximum(self):
        return self._getNumber(7)

    def setMaximum(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(QuestProgressItemModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('eventType', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('desc', '')
        self._addStringProperty('rewards', '')
        self._addNumberProperty('value', 0)
        self._addStringProperty('deltaLabel', '')
        self._addNumberProperty('maximum', 0)
