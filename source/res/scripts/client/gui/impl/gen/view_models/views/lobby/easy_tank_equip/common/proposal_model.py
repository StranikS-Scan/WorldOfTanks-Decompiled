# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/common/proposal_model.py
import typing
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
T = typing.TypeVar('T')

class ProposalDisableReason(Enum):
    NONE = 'none'
    NOT_FORMED = 'notFormed'
    BUILT_IN_STYLE = 'builtInStyle'


class ProposalType(Enum):
    NONE = 'none'
    CREW = 'crew'
    OPT_DEVICES = 'optDevices'
    SHELLS = 'shells'
    CONSUMABLES = 'consumables'
    STYLES = 'styles'


class ProposalModel(ViewModel, typing.Generic[T]):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ProposalModel, self).__init__(properties=properties, commands=commands)

    def getSelected(self):
        return self._getBool(0)

    def setSelected(self, value):
        self._setBool(0, value)

    def getDisableReason(self):
        return ProposalDisableReason(self._getString(1))

    def setDisableReason(self, value):
        self._setString(1, value.value)

    def getPresetIndex(self):
        return self._getNumber(2)

    def setPresetIndex(self, value):
        self._setNumber(2, value)

    def getPresets(self):
        return self._getArray(3)

    def setPresets(self, value):
        self._setArray(3, value)

    @staticmethod
    def getPresetsType():
        return T

    def _initialize(self):
        super(ProposalModel, self)._initialize()
        self._addBoolProperty('selected', False)
        self._addStringProperty('disableReason')
        self._addNumberProperty('presetIndex', 0)
        self._addArrayProperty('presets', Array())
