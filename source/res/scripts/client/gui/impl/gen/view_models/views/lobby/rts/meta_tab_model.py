# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/meta_tab_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Tabs(Enum):
    COLLECTION = 'collection'
    QUESTS = 'quests'
    STATISTICS = 'statistics'
    LEADERBOARD = 'leaderboard'


class MetaTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MetaTabModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return Tabs(self._getString(0))

    def setName(self, value):
        self._setString(0, value.value)

    def getResId(self):
        return self._getNumber(1)

    def setResId(self, value):
        self._setNumber(1, value)

    def getShowNotificationBubble(self):
        return self._getBool(2)

    def setShowNotificationBubble(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(MetaTabModel, self)._initialize()
        self._addStringProperty('name')
        self._addNumberProperty('resId', 0)
        self._addBoolProperty('showNotificationBubble', False)
