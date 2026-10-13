# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/battle/portal_widget_boss.py
from frameworks.wulf import ViewModel

class PortalWidgetBoss(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalWidgetBoss, self).__init__(properties=properties, commands=commands)

    def getCurrentHealth(self):
        return self._getNumber(0)

    def setCurrentHealth(self, value):
        self._setNumber(0, value)

    def getMaxHealth(self):
        return self._getNumber(1)

    def setMaxHealth(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PortalWidgetBoss, self)._initialize()
        self._addNumberProperty('currentHealth', 0)
        self._addNumberProperty('maxHealth', 10)
