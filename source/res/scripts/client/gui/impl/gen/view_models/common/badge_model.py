# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/badge_model.py
from frameworks.wulf import ViewModel

class BadgeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BadgeModel, self).__init__(properties=properties, commands=commands)

    def getBadgeID(self):
        return self._getString(0)

    def setBadgeID(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getString(1)

    def setLevel(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BadgeModel, self)._initialize()
        self._addStringProperty('badgeID', '')
        self._addStringProperty('level', '')
