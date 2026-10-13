# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/battle/portal_widget_camp.py
from enum import Enum
from frameworks.wulf import ViewModel

class CampState(Enum):
    CANBECAPTURED = 'canBeCaptured'
    CAPTURED = 'captured'
    DEFAULT = 'default'


class PortalWidgetCamp(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PortalWidgetCamp, self).__init__(properties=properties, commands=commands)

    def getAllDefenders(self):
        return self._getNumber(0)

    def setAllDefenders(self, value):
        self._setNumber(0, value)

    def getKilledDefenders(self):
        return self._getNumber(1)

    def setKilledDefenders(self, value):
        self._setNumber(1, value)

    def getState(self):
        return CampState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(PortalWidgetCamp, self)._initialize()
        self._addNumberProperty('allDefenders', 0)
        self._addNumberProperty('killedDefenders', 0)
        self._addStringProperty('state')
