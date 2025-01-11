# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_trigger_hint_tabs_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MenuTriggerHints(Enum):
    GUESTA = 'guestA'
    TOURNAMENT = 'tournament'
    DECORATIONZONES = 'DecorationZones'
    NONE = 'none'


class NyTriggerHintTabsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyTriggerHintTabsModel, self).__init__(properties=properties, commands=commands)

    def getActiveTabs(self):
        return self._getArray(0)

    def setActiveTabs(self, value):
        self._setArray(0, value)

    @staticmethod
    def getActiveTabsType():
        return unicode

    def getTriggerHintType(self):
        return MenuTriggerHints(self._getString(1))

    def setTriggerHintType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(NyTriggerHintTabsModel, self)._initialize()
        self._addArrayProperty('activeTabs', Array())
        self._addStringProperty('triggerHintType')
