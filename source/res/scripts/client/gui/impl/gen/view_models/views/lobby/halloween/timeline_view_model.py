# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/timeline_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.tank_model import TankModel
from gui.impl.gen.view_models.views.lobby.halloween.timeline_item_model import TimelineItemModel

class StateEnum(Enum):
    DEFAULT = 'default'
    ALL_RECEIVED = 'allReceived'


class ButtonIdEnum(IntEnum):
    PLAY = 9
    TANK = 8


class TimelineViewModel(ViewModel):
    __slots__ = ('onDebugClick', 'onClick')

    def __init__(self, properties=5, commands=2):
        super(TimelineViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def timelineTank(self):
        return self._getViewModel(0)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getSelectedItemId(self):
        return self._getNumber(2)

    def setSelectedItemId(self, value):
        self._setNumber(2, value)

    def getItems(self):
        return self._getArray(3)

    def setItems(self, value):
        self._setArray(3, value)

    def getState(self):
        return StateEnum(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(TimelineViewModel, self)._initialize()
        self._addViewModelProperty('timelineTank', TankModel())
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('selectedItemId', 0)
        self._addArrayProperty('items', Array())
        self._addStringProperty('state')
        self.onDebugClick = self._addCommand('onDebugClick')
        self.onClick = self._addCommand('onClick')
