# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/catalog/breadcrumb_model.py
from frameworks.wulf import ViewModel

class BreadcrumbModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BreadcrumbModel, self).__init__(properties=properties, commands=commands)

    def getAchievementId(self):
        return self._getNumber(0)

    def setAchievementId(self, value):
        self._setNumber(0, value)

    def getKey(self):
        return self._getString(1)

    def setKey(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BreadcrumbModel, self)._initialize()
        self._addNumberProperty('achievementId', 0)
        self._addStringProperty('key', '')
