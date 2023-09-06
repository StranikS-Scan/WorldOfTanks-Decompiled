# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/tab_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class MetaRootViews(IntEnum):
    PROGRESSION = 0
    RANKREWARDS = 1
    WEEKLYQUESTS = 2
    LEADERBOARD = 3


class TabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TabModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return MetaRootViews(self._getNumber(0))

    def setId(self, value):
        self._setNumber(0, value.value)

    def getHasNotification(self):
        return self._getBool(1)

    def setHasNotification(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(TabModel, self)._initialize()
        self._addNumberProperty('id')
        self._addBoolProperty('hasNotification', False)
