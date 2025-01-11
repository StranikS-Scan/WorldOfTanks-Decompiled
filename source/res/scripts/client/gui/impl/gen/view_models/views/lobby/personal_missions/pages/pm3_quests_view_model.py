# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quests_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_line_model import Pm3QuestsLineModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_page_tab_model import Pm3QuestsPageTabModel

class OperationState(Enum):
    LOCKED = 'locked'
    LOCKEDNOVEHICLE = 'lockedNoVehicle'
    ACTIVE = 'active'
    ALERT = 'alert'
    COMPLETEWITHHONOR = 'completeWithHonor'
    COMPLETE = 'complete'


class CardState(Enum):
    SWITCH = 'switch'
    NOTAVAILABLE = 'notAvailable'
    AVAILABLE = 'available'
    PAUSE = 'pause'
    INPROGRESS = 'inProgress'
    DONES = 'doneSwitch'
    DONE = 'done'
    DONEP = 'donePause'
    DONEH = 'doneHonor'


class Pm3QuestsViewModel(ViewModel):
    __slots__ = ('switchTab', 'backToOperation', 'openVehicleViewWindow')

    def __init__(self, properties=9, commands=3):
        super(Pm3QuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestsLines(self):
        return self._getArray(0)

    def setQuestsLines(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsLinesType():
        return Pm3QuestsLineModel

    def getState(self):
        return OperationState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getOperationName(self):
        return self._getString(2)

    def setOperationName(self, value):
        self._setString(2, value)

    def getOperationId(self):
        return self._getNumber(3)

    def setOperationId(self, value):
        self._setNumber(3, value)

    def getMinVehicleLevel(self):
        return self._getNumber(4)

    def setMinVehicleLevel(self, value):
        self._setNumber(4, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(5)

    def setMaxVehicleLevel(self, value):
        self._setNumber(5, value)

    def getPrevOperationName(self):
        return self._getString(6)

    def setPrevOperationName(self, value):
        self._setString(6, value)

    def getIsSwitched(self):
        return self._getBool(7)

    def setIsSwitched(self, value):
        self._setBool(7, value)

    def getTabs(self):
        return self._getArray(8)

    def setTabs(self, value):
        self._setArray(8, value)

    @staticmethod
    def getTabsType():
        return Pm3QuestsPageTabModel

    def _initialize(self):
        super(Pm3QuestsViewModel, self)._initialize()
        self._addArrayProperty('questsLines', Array())
        self._addStringProperty('state')
        self._addStringProperty('operationName', '')
        self._addNumberProperty('operationId', 0)
        self._addNumberProperty('minVehicleLevel', 0)
        self._addNumberProperty('maxVehicleLevel', 0)
        self._addStringProperty('prevOperationName', '')
        self._addBoolProperty('isSwitched', False)
        self._addArrayProperty('tabs', Array())
        self.switchTab = self._addCommand('switchTab')
        self.backToOperation = self._addCommand('backToOperation')
        self.openVehicleViewWindow = self._addCommand('openVehicleViewWindow')
